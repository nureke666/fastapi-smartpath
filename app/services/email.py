def send_email_simulation(to_email: str, subject: str, body: str):
    """
    Имитация отправки email. Пишет содержимое в консоль сервера.
    """
    print("\n" + "="*60)
    print(f"📧 [EMAIL SERVICE SIMULATION]")
    print(f"TO:      {to_email}")
    print(f"FROM:    noreply@smartpath.mvp")
    print(f"SUBJECT: {subject}")
    print("-" * 60)
    print(body)
    print("="*60 + "\n")
    return True