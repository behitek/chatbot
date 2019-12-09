## Usage

- customer_id: ['KH01', 'KH02', 'KH03', 'KH04']

```python
from after_sale import BotAfterSale

bot = BotAfterSale.Bot()

res = bot.interactive(customer_id='KH01', message='msg')
print(res)
```

