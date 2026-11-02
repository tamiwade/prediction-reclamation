import subprocess
import sys
import os
import urllib.request
import json
import getpass

GIT = r"C:\Program Files\Git\bin\git.exe"

def run(cmd, check=True):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if check and result.returncode != 0:
        return False
    return True

def create_repo_api(username, token, repo_name):
    """Crée le dépôt GitHub via l'API REST"""
    url = "https://api.github.com/user/repos"
    data = json.dumps({
        "name": repo_name,
        "description": "Application de prédiction de réclamations automobiles - Machine Learning",
        "private": False,
        "auto_init": False
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            return True, body.get("html_url", "")
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        msg = body.get("message", str(e))
        if "already exists" in msg or "name already exists" in msg:
            return True, f"https://github.com/{username}/{repo_name}"
        return False, msg

def main():
    os.system("cls")
    print("=" * 60)
    print("  DÉPLOIEMENT AUTOMATIQUE - Prédiction Réclamations ML")
    print("=" * 60)
    print()

    # Récupérer les infos
    username = input("👤 Ton nom d'utilisateur GitHub : ").strip()
    print()
    print("🔑 Ton Personal Access Token GitHub")
    print("   (GitHub → Settings → Developer settings → Personal access tokens")
    print("    → Tokens classic → Generate new token → coche 'repo')")
    print()
    token = getpass.getpass("   Colle ton token (invisible pour sécurité) : ").strip()
    print()

    repo_name = "prediction-reclamation"

    # Étape 1 : Créer le dépôt sur GitHub via API
    print("📦 Création du dépôt sur GitHub...")
    ok, result = create_repo_api(username, token, repo_name)
    if ok:
        print(f"   ✅ Dépôt prêt : {result}")
    else:
        print(f"   ❌ Erreur API : {result}")
        print("      Crée le dépôt manuellement sur https://github.com/new")
        print(f"      Nom : {repo_name} | Visibilité : Public")
        input("\nAppuie sur Entrée une fois le dépôt créé manuellement...")

    print()

    # Étape 2 : Init git local
    print("🔧 Initialisation du dépôt local...")
    run([GIT, "init"], check=False)
    run([GIT, "config", "user.name", username], check=False)
    run([GIT, "config", "user.email", f"{username}@users.noreply.github.com"], check=False)

    # Étape 3 : Add & commit
    print()
    print("📁 Ajout des fichiers...")
    run([GIT, "add", "."])
    # Vérifier s'il y a quelque chose à committer
    result = subprocess.run([GIT, "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout.strip():
        run([GIT, "commit", "-m", "Initial commit - Application de prediction de reclamations ML"])
    else:
        # Peut-être qu'il y a déjà des commits
        print("   (fichiers déjà committés ou pas de changement)")

    # Étape 4 : Remote & push
    print()
    print("🚀 Envoi vers GitHub...")
    remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    run([GIT, "remote", "remove", "origin"], check=False)
    run([GIT, "remote", "add", "origin", remote_url])
    run([GIT, "branch", "-M", "main"], check=False)
    ok = run([GIT, "push", "-u", "origin", "main"])

    print()
    if ok:
        print("=" * 60)
        print("  ✅ SUCCÈS ! Ton code est sur GitHub !")
        print()
        print(f"  🔗 Dépôt : https://github.com/{username}/{repo_name}")
        print()
        print("  ➡️  PROCHAINE ÉTAPE - Streamlit Cloud :")
        print("     1. Va sur https://share.streamlit.io")
        print("     2. Connecte-toi avec GitHub")
        print("     3. Clique 'New app'")
        print(f"     4. Repository : {username}/{repo_name}")
        print("     5. Branch : main")
        print("     6. Main file : app.py")
        print("     7. Clique Deploy!")
        print("=" * 60)
        print()
        # Ouvrir Streamlit Cloud automatiquement
        os.startfile("https://share.streamlit.io")
    else:
        print("❌ Échec du push. Vérifications :")
        print("   - Le token a bien la permission 'repo' cochée")
        print("   - Le nom d'utilisateur est correct")
        print(f"   - Le dépôt {repo_name} existe sur ton GitHub")

    print()
    input("Appuie sur Entrée pour fermer...")

if __name__ == "__main__":
    main()
