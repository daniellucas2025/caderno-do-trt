# -*- coding: utf-8 -*-
"""
Publicador Oficial do Site no GitHub Pages
Tribunal: TRT-4 (Rio Grande do Sul)
"""

import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    print("=" * 65)
    print("   [2] PUBLICANDO SITE NO GITHUB PAGES...")
    print("=" * 65)

    scripts_dir = Path(__file__).resolve().parent
    trt_dir = scripts_dir.parent                     # TRT-04-RS
    caderno_root = trt_dir.parent                   # caderno-do-trt
    project_goo = caderno_root.parent               # Project Goo

    plataforma_dir = trt_dir / "Plataforma"
    index_origem = plataforma_dir / "index.html"

    if not index_origem.exists():
        print(f"❌ Erro: index.html não encontrado em:")
        print(f"   {plataforma_dir}")
        print("\n💡 Dica: Execute primeiro o script '1. GERAR_PLATAFORMA.bat' para compilar o site.")
        sys.exit(1)

    print(f"✅ Arquivo compilado encontrado: {index_origem}")

    # 1. Atualizar repositório online metas-trt4 (onde o site GitHub Pages está hospedado)
    metas_site_dir = project_goo / "unificador-html-estudos" / "METAS"
    if metas_site_dir.exists() and (metas_site_dir / ".git").exists():
        print(f"\n📦 Atualizando site no repositório GitHub Pages:")
        print(f"   Destino: {metas_site_dir}")
        
        # Copiar index.html atualizado
        shutil.copy2(index_origem, metas_site_dir / "index.html")
        
        # Remover duplicatas antigas se ainda existirem
        for arq_velho in ["Plataforma_Metas.html", "Estudos_Unificado.html"]:
            velho_path = metas_site_dir / arq_velho
            if velho_path.exists():
                velho_path.unlink()
        
        status = subprocess.run(["git", "status", "--porcelain"], cwd=str(metas_site_dir), capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if not status.stdout.strip():
            print("ℹ️  O site metas-trt4 já está 100% atualizado com a versão mais recente.")
        else:
            print("🔄 Enviando novidades para o GitHub (metas-trt4)...")
            subprocess.run(["git", "add", "-A"], cwd=str(metas_site_dir), check=True)
            hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            subprocess.run(["git", "commit", "-m", f"Atualização da plataforma ({hora})"], cwd=str(metas_site_dir), check=True)
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=str(metas_site_dir), capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if push_res.returncode == 0:
                print("✅ Enviado com sucesso para o GitHub Pages!")
            else:
                print("⚠️ Aviso ao enviar para GitHub:", push_res.stderr.strip())

    # 2. Registrar alterações no repositório local caderno-do-trt
    if (caderno_root / ".git").exists():
        print(f"\n📦 Verificando repositório principal: {caderno_root.name}")
        status = subprocess.run(["git", "status", "--porcelain"], cwd=str(caderno_root), capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if status.stdout.strip():
            print("🔄 Registrando alterações locais no Git...")
            subprocess.run(["git", "add", "-A"], cwd=str(caderno_root), check=True)
            hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            subprocess.run(["git", "commit", "-m", f"Atualização da plataforma {trt_dir.name} ({hora})"], cwd=str(caderno_root), check=True)
            print("✅ Alterações salvas no histórico do repositório local!")

    print("\n" + "=" * 65)
    print("   🎉 ETAPA 2 CONCLUÍDA: Site no ar!")
    print("   🌐 ACESSE O SITE:")
    print("   👉 https://daniellucas2025.github.io/metas-trt4/")
    print("=" * 65)

if __name__ == "__main__":
    main()
