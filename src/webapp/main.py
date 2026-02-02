"""
FastAPI web app for descriptive statistics.
"""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from typing import Dict, Any

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from data_loading.factory import create_reader, load_implementations
from domain.dataset import DataSet


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
OUTPUT_BASE = Path("output") / "web_runs"

app = FastAPI(title="Descriptive Statistics Web")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    data_file: UploadFile = File(...),
    generate_charts: bool = Form(True),
    generate_pdfs: bool = Form(True),
    generate_bivariate: bool = Form(True),
    detect_artificial: bool = Form(True),
    generate_final_report: bool = Form(True),
    # univariate generator
    uni_enabled: bool = Form(False),
    uni_var: str = Form(""),
    uni_n: int = Form(0),
    uni_method: str = Form("fit"),
    uni_dist: str = Form(""),
    uni_mean: str = Form(""),
    uni_std: str = Form(""),
    # bivariate generator
    bi_enabled: bool = Form(False),
    bi_x: str = Form(""),
    bi_y: str = Form(""),
    bi_n: int = Form(0),
    bi_corr: str = Form(""),
    bi_mode: str = Form("copula"),
    bi_dist_x: str = Form(""),
    bi_dist_y: str = Form(""),
):
    load_implementations()

    if not data_file.filename:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Nenhum arquivo enviado."},
            status_code=400,
        )

    extension = Path(data_file.filename).suffix.lower().lstrip(".")
    if extension not in {"csv", "xlsx"}:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Formato inválido. Use CSV ou XLSX."},
            status_code=400,
        )

    run_id = uuid4().hex[:8]
    upload_dir = OUTPUT_BASE / f"uploads_{run_id}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = upload_dir / data_file.filename

    with open(upload_path, "wb") as f:
        f.write(await data_file.read())

    try:
        reader = create_reader(extension, str(upload_path))
        df = reader.read()
        dataset_name = f"{Path(data_file.filename).stem}_{run_id}"
        dataset = DataSet(df, name=dataset_name)

        # optional generators
        if uni_enabled and uni_var and uni_n > 0:
            dataset.generate_univariate_synthetic(
                uni_var,
                n=uni_n,
                method=uni_method,
                dist_name=uni_dist or None,
                mean=_to_float_or_none(uni_mean),
                std=_to_float_or_none(uni_std),
            )

        if bi_enabled and bi_x and bi_y and bi_n > 0:
            dataset.generate_bivariate_synthetic(
                bi_x,
                bi_y,
                n=bi_n,
                target_corr=_to_float_or_none(bi_corr),
                mode=bi_mode,
                dist_x=bi_dist_x or None,
                dist_y=bi_dist_y or None,
            )

        output_dir = dataset.export_all(
            output_base_dir=OUTPUT_BASE,
            generate_charts=generate_charts,
            generate_pdfs=generate_pdfs,
            generate_bivariate=generate_bivariate,
            detect_artificial=detect_artificial,
            generate_final_report=generate_final_report,
        )

        files = _list_output_files(output_dir)
        context: Dict[str, Any] = {
            "request": request,
            "run_id": output_dir.name,
            "files": files,
            "output_dir": str(output_dir),
        }
        return templates.TemplateResponse("result.html", context)
    except Exception as exc:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Erro ao processar: {exc}"},
            status_code=500,
        )


@app.get("/download/{run_id}/{filename}")
def download(run_id: str, filename: str):
    safe_name = Path(filename).name
    output_dir = OUTPUT_BASE / run_id
    file_path = output_dir / safe_name
    if not file_path.exists():
        return RedirectResponse(url="/")
    return FileResponse(file_path)


def _list_output_files(output_dir: Path):
    files = []
    for path in output_dir.glob("*"):
        if path.is_file():
            files.append(path.name)
    return sorted(files)


def _to_float_or_none(value: str):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None
