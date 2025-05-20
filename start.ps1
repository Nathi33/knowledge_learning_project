# start.ps1
Write-Host "Démarrage de Stripe listen..."
Start-Process powershell -ArgumentList "stripe listen --forward-to localhost:8000/payments/webhook/" -WindowStyle Minimized

Start-Sleep -Seconds 2

Write-Host "Démarrage du serveur Django..."
python manage.py runserver

# Lancement de mon projet : .\start.ps1
