"""
Gerador de PDFs a partir de relatórios Markdown.

Converte relatórios .md em PDFs profissionais com:
- Tabelas formatadas
- Imagens embutidas
- Estilo profissional
- Quebras de página adequadas
"""

import markdown
from pathlib import Path
from weasyprint import HTML, CSS
from typing import Optional
import base64


class PDFGenerator:
    """Gera PDFs profissionais a partir de arquivos Markdown."""

    # CSS profissional para os relatórios
    REPORT_CSS = """
    @page {
        size: A4;
        margin: 2cm;
        @bottom-center {
            content: "Página " counter(page) " de " counter(pages);
            font-size: 9pt;
            color: #666;
        }
    }

    body {
        font-family: 'DejaVu Sans', 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
        max-width: 100%;
    }

    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        margin-top: 20px;
        font-size: 24pt;
    }

    h2 {
        color: #34495e;
        border-bottom: 2px solid #95a5a6;
        padding-bottom: 8px;
        margin-top: 18px;
        font-size: 18pt;
        page-break-after: avoid;
    }

    h3 {
        color: #7f8c8d;
        margin-top: 14px;
        font-size: 14pt;
        page-break-after: avoid;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
        font-size: 10pt;
        page-break-inside: avoid;
    }

    th {
        background-color: #3498db;
        color: white;
        padding: 12px 8px;
        text-align: left;
        font-weight: bold;
    }

    td {
        padding: 10px 8px;
        border-bottom: 1px solid #ddd;
    }

    tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    tr:hover {
        background-color: #e9ecef;
    }

    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 20px auto;
        page-break-inside: avoid;
    }

    ul, ol {
        margin: 10px 0;
        padding-left: 30px;
    }

    li {
        margin: 5px 0;
    }

    strong {
        color: #2c3e50;
        font-weight: bold;
    }

    em {
        color: #7f8c8d;
        font-style: italic;
    }

    hr {
        border: none;
        border-top: 2px solid #ecf0f1;
        margin: 20px 0;
    }

    code {
        background-color: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
    }

    blockquote {
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin-left: 0;
        color: #555;
        font-style: italic;
    }

    /* Estilo para interpretações */
    p {
        margin: 8px 0;
        text-align: justify;
    }

    /* Destaque para valores importantes */
    table strong {
        color: #e74c3c;
    }

    /* Evitar quebras de página inadequadas */
    h1, h2, h3, h4 {
        page-break-after: avoid;
    }

    table, figure, img {
        page-break-inside: avoid;
    }
    """

    def __init__(self, output_dir: Path):
        """
        Inicializa o gerador de PDFs.

        Args:
            output_dir: Diretório onde os PDFs serão salvos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _embed_images_in_html(self, html_content: str, md_file_path: Path) -> str:
        """
        Converte referências de imagens relativas em imagens base64 embutidas.

        Args:
            html_content: Conteúdo HTML com referências de imagens
            md_file_path: Caminho do arquivo Markdown original (para resolver caminhos relativos)

        Returns:
            HTML com imagens embutidas em base64
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, 'html.parser')

        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not src.startswith(('http://', 'https://', 'data:')):
                # Caminho relativo - resolver baseado no diretório do .md
                img_path = md_file_path.parent / src

                if img_path.exists():
                    # Ler imagem e converter para base64
                    try:
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            # Detectar tipo de imagem
                            ext = img_path.suffix.lower()
                            mime_type = {
                                '.png': 'image/png',
                                '.jpg': 'image/jpeg',
                                '.jpeg': 'image/jpeg',
                                '.gif': 'image/gif',
                                '.svg': 'image/svg+xml'
                            }.get(ext, 'image/png')

                            # Substituir src por data URI
                            img['src'] = f"data:{mime_type};base64,{img_data}"
                    except Exception as e:
                        print(f"⚠️  Erro ao embutir imagem {img_path}: {e}")

        return str(soup)

    def markdown_to_pdf(
        self,
        md_file_path: Path,
        pdf_file_path: Optional[Path] = None,
        title: Optional[str] = None
    ) -> Path:
        """
        Converte um arquivo Markdown para PDF.

        Args:
            md_file_path: Caminho do arquivo .md
            pdf_file_path: Caminho de saída do PDF (opcional, usa mesmo nome do .md)
            title: Título do documento (opcional, usa nome do arquivo)

        Returns:
            Caminho do arquivo PDF gerado
        """
        # Define caminho de saída
        if pdf_file_path is None:
            pdf_file_path = self.output_dir / f"{md_file_path.stem}.pdf"

        # Lê o Markdown
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Converte Markdown para HTML
        md_processor = markdown.Markdown(extensions=[
            'tables',           # Suporte a tabelas
            'fenced_code',      # Blocos de código
            'nl2br',            # Quebras de linha
            'sane_lists'        # Listas melhoradas
        ])
        html_body = md_processor.convert(md_content)

        # Cria HTML completo com título
        doc_title = title or md_file_path.stem.replace('_', ' ').title()
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>{doc_title}</title>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        # Embute imagens no HTML
        html_content = self._embed_images_in_html(html_content, md_file_path)

        # Gera PDF
        try:
            HTML(string=html_content, base_url=str(md_file_path.parent)).write_pdf(
                pdf_file_path,
                stylesheets=[CSS(string=self.REPORT_CSS)]
            )
            return pdf_file_path
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar PDF: {e}")

    def generate_all_pdfs(self, source_dir: Path) -> list[Path]:
        """
        Gera PDFs para todos os arquivos .md em um diretório.

        Args:
            source_dir: Diretório contendo arquivos .md

        Returns:
            Lista de caminhos dos PDFs gerados
        """
        pdf_files = []

        md_files = list(Path(source_dir).glob('*.md'))

        for md_file in md_files:
            try:
                pdf_path = self.markdown_to_pdf(md_file)
                pdf_files.append(pdf_path)
                print(f"✓ PDF gerado: {pdf_path.name}")
            except Exception as e:
                print(f"✗ Erro ao gerar PDF de {md_file.name}: {e}")

        return pdf_files
