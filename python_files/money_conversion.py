# PHP Currency to USD Conversion Module

while True:
  print('Convert Peso to Dollar\n')
  print('Select a currency you want to convert\n')

  print('A. Peso')
  print('B. Dollar\n')

  selected_currency = input('Enter your choice (A/B): ')

# NOTE - USD To PHP Conversion 
  if selected_currency.upper() == 'A':
    peso_amount = float(input('Enter your peso amount: ₱'))
    print('\nConverting...\n')
    conversion_rate = 0.070  # Example conversion rate
    dollar_amount = peso_amount * conversion_rate
    print(f' -------- {peso_amount} PHP is equal to {dollar_amount:.2f} USD --------')
    break
  # NOTE - USD To PHP Conversion 
  elif selected_currency.upper() == 'B':
    dollar_amount = float(input('Enter your dollar amount: $'))
    print('\nConverting...\n')
    conversion_rate = 58.77  # Example conversion rate
    peso_amount = dollar_amount * conversion_rate
    print(f' -------- {dollar_amount} USD is equal to {peso_amount:.2f} PHP -------- ')
    break
  else:
    print('Invalid selection. Please choose A or B.\n')
