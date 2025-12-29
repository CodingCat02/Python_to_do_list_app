# PHP Currency to USD Conversion Module

print('Convert Peso to Dollar')
print('Select a currency you want to convert')
print('A. Peso')

print('B. Dollar')

selected_currency = input('Enter your choice (A/B): ')

# NOTE - USD To PHP Conversion 
if selected_currency.upper() == 'A':
    peso_amount = float(input('Enter your peso amount: '))
    conversion_rate = 0.070  # Example conversion rate
    dollar_amount = peso_amount * conversion_rate
    print(f'{peso_amount} PHP is equal to {dollar_amount:.2f} USD')
    
# NOTE - USD To PHP Conversion 
elif selected_currency.upper() == 'B':
    dollar_amount = float(input('Enter your dollar amount: '))
    conversion_rate = 58.77  # Example conversion rate
    peso_amount = dollar_amount * conversion_rate
    print(f'{dollar_amount} USD is equal to {peso_amount:.2f} PHP')

else:
    print('Invalid selection. Please choose A or B.')
