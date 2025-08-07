from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def models_keyboard(models) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=m)] for m in models]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def sizes_keyboard() -> ReplyKeyboardMarkup:
    sizes = ["XS", "S", "M", "L", "XL"]
    keyboard = [[KeyboardButton(text=s)] for s in sizes]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def paid_keyboard(order_id: str) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="Я оплатил", callback_data=f"paid:{order_id}")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
