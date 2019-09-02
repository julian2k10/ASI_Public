import logging
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

port = 465
sender_email = "market_advisor48@gmail.com"
admin_email = 'johnsmith32@gmail.com'
contacts_list = ['jane_smith1@gmail.com', 'jane_smith2@gmail.com', 'jane_smith3@gmail.com', 'jane_smith45@yahoo.com']
password = 'password343$$'

#add list item with company info to html
def add_html_list_item(html, name, symbol, rank, rating, intrinsic_value, revenue_growth):
    url =f'https://finance.yahoo.com/quote/{symbol}?p={symbol}'
    if rating != 'None':
        rating = float(rating)
    else:
        rating = 0

    if revenue_growth != 'None':
        revenue_growth = float(revenue_growth)
    else:
        revenue_growth = 0
    html.append("\n\t\t<li>")
    html.append(f"\n\t\t\t<h3>{name} - (<a href={url}>{symbol}</a>) </h3>")
    html.append(f"\n\t\t\t<label>Rank : {rank}</label><br>")
    html.append(f"\n\t\t\t<label>Rating : {rating:.0f}</label><br>")
    html.append(f"\n\t\t\t<label>Intrinsic Value : {intrinsic_value:.0f}</label><br>")
    html.append(f"\n\t\t\t<label>Revenue Growth Rate : {revenue_growth:.2f}%</label><br>")
    html.append("\n\t\t</li>")
    
#create html message text from company object
def create_simple_html_message(title, text):
    html = list()
    html.append("\n<html>")
    html.append("\n\t<body>")
    html.append(f"\n\t<h1>{title}</h1>")
    html.append(f"\n\t<p>{text}</p>")
    html.append("\n\t</body>")
    html.append("\n</html>")
    #html.append("\n\"\"\"")
    html = ''.join(html)

    return html

def create_html_message(companies, sector, sorted_keys='None'):
    html = list()
    #html.append("\"\"\"\\")
    html.append("\n<html>")
    html.append("\n\t<body>")
    html.append(f"\n\t<h1>Top 10 {sector} Stocks</h1>")
    html.append("\n\t<ul>")

    if sorted_keys == 'None':
        sorted_keys = list(companies.keys())
        
    for industry in sorted_keys:
        html.append(f"\n\t\t<h2>Industry : {industry}</h2>")
        html.append("\n\t\t<ol>")
        for x in range(len(companies[industry])):
            company = companies[industry][x]
            if isinstance(company, dict):
                add_html_list_item(html, company['Name'], company['Symbol'], company['Rank'], company['Rating'], company['Intrinsic Value'], company['3 Year Revenue Growth(Annual)'])
            else:
                continue
           
        html.append("\n\t\t</ol>") 
    html.append("\n\t</ul>")
    html.append("\n\t</body>")
    html.append("\n</html>")
    #html.append("\n\"\"\"")
    html = ''.join(html)
    
    return html

#send html group messages 
def send_html_messages(plain_text, html_text):
    message = MIMEMultipart("alternative")
    part1 = MIMEText(plain_text, "plain")
    part2 = MIMEText(html_text, "html")

    message["Subject"] = "Stock Market Update"
    message["From"] = sender_email

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        for receiver_email in contacts_list:
            message["To"] = receiver_email
            print(f'sending email to {receiver_email} ...')
            server.sendmail(sender_email, receiver_email, message.as_string())

def send_html_message(plain_text, html_text):
    message = MIMEMultipart("alternative")
    part1 = MIMEText(plain_text, "plain")
    part2 = MIMEText(html_text, "html")

    message["Subject"] = "Stock Market Update"
    message["From"] = sender_email

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        message["To"] = admin_email
        print(f'sending email to {admin_email} ...')
        server.sendmail(sender_email, admin_email, message.as_string())