import sys
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

    base_dir = Path(__file__).resolve().parent
    if (base_dir / "unificador-html-estudos").exists():
        metas_dir = base_dir / "unificador-html-estudos" / "METAS"
    else:
        metas_dir = base_dir / "METAS"

    if not metas_dir.exists():
        print(f"❌ Erro: Pasta METAS não encontrada em: {metas_dir}")
        sys.exit(1)

    print("\n📦 Verificando alterações no repositório Git...")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=str(metas_dir), capture_output=True, text=True, encoding='utf-8', errors='ignore')

    if not status.stdout.strip():
        print("ℹ️  O site já está 100% atualizado com a versão mais recente no GitHub.")
    else:
        print("🔄 Enviando novidades para o GitHub (main)...")
        subprocess.run(["git", "add", "-A"], cwd=str(metas_dir), check=True)
        hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        subprocess.run(["git", "commit", "-m", f"Atualização do site ({hora})"], cwd=str(metas_dir), check=True)
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=str(metas_dir), capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if push_res.returncode != 0:
            print("❌ Erro ao enviar para o GitHub:")
            print(push_res.stderr)
            sys.exit(1)
        print("✅ Enviado com sucesso para o GitHub!")

    print("\n" + "=" * 65)
    print("   🎉 ETAPA 2 CONCLUÍDA: Site no ar!")
    print("   🌐 ACESSE O SITE:")
    print("   👉 https://daniellucas2025.github.io/metas-trt7/")
    print("=" * 65)

if __name__ == "__main__":
    main()

