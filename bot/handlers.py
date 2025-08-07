from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime

import config
import db
from keyboards import models_keyboard, sizes_keyboard, paid_keyboard
from models import PRODUCTS, Order
import utils

router = Router()


class OrderForm(StatesGroup):
    product = State()
    size = State()
    contact = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Давайте закажем футболку.\nВыберите модель:",
        reply_markup=models_keyboard(PRODUCTS.keys()),
    )
    await state.set_state(OrderForm.product)


@router.message(OrderForm.product)
async def choose_product(message: Message, state: FSMContext):
    if message.text not in PRODUCTS:
        await message.answer("Пожалуйста, выберите модель из списка.")
        return
    await state.update_data(product=message.text)
    await message.answer("Выберите размер:", reply_markup=sizes_keyboard())
    await state.set_state(OrderForm.size)


@router.message(OrderForm.size)
async def choose_size(message: Message, state: FSMContext):
    if message.text not in ["XS", "S", "M", "L", "XL"]:
        await message.answer("Пожалуйста, выберите размер из списка.")
        return
    await state.update_data(size=message.text)
    await message.answer(
        "Введите номер телефона или имя и адрес для связи:",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(OrderForm.contact)


@router.message(OrderForm.contact)
async def get_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    product = data["product"]
    size = data["size"]
    order_id = utils.generate_order_id()
    order = Order(
        id=order_id,
        telegram_id=message.from_user.id,
        product_name=product,
        size=size,
        contact=message.text,
        status="created",
        created_at=datetime.utcnow().isoformat(),
    )
    await db.create_order(order)
    price = PRODUCTS[product]
    text = (
        f"Заказ оформлен! Переведите {price} ₽ на карту {config.SBER_CARD}\n"
        f"В комментарии к переводу укажите: `{order_id}`\n"
        "После оплаты нажмите кнопку ниже."
    )
    await message.answer(text, reply_markup=paid_keyboard(order_id), parse_mode="Markdown")
    await state.clear()


@router.callback_query(F.data.startswith("paid:"))
async def paid_callback(callback: CallbackQuery):
    order_id = callback.data.split(":")[1]
    order = await db.get_order(order_id)
    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return
    await db.update_status(order_id, "waiting_confirmation")
    await callback.message.answer("Спасибо! Мы уведомили администратора о платеже.")
    await callback.answer()
    await callback.bot.send_message(
        config.ADMIN_ID, f"Заказ {order_id} ожидает подтверждения."
    )


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    orders = await db.get_orders_by_status("waiting_confirmation")
    if not orders:
        await message.answer("Нет новых заказов.")
        return
    lines = [
        f"{o.id}: {o.product_name} {o.size}, {o.contact}"
        for o in orders
    ]
    await message.answer("Новые заказы:\n" + "\n".join(lines))


@router.message(Command("подтвердить"))
async def confirm_order(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Используйте: /подтвердить <order_id>")
        return
    order_id = parts[1]
    order = await db.get_order(order_id)
    if not order:
        await message.answer("Заказ не найден.")
        return
    await db.update_status(order_id, "paid")
    await message.bot.send_message(
        order.telegram_id,
        "Спасибо, оплата подтверждена. Мы свяжемся с вами в течение суток.",
    )
    await message.answer(f"Заказ {order_id} отмечен как оплаченный.")
