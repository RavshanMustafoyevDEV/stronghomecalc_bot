import logging
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio


API_TOKEN = '5309386583:AAHYsnEXzDMzVhy2tXPu6I1az242DsNSVpQ'

# Log konfiguratsiyasi
logging.basicConfig(level=logging.INFO)

# Bot va saqlashni inicializatsiya qilish
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()

# Router va Dispatcher yaratish
router = Router()
dp = Dispatcher(storage=storage)
dp.include_router(router)

# Xonadon narxini hisoblash uchun state-lar
class PriceCalculation(StatesGroup):
    price_per_m2 = State()
    area = State()
    rooms = State()
    floor_level = State()
    down_payment_percentage = State()
    installment_months = State()
    discount_amount = State()

# /calculate buyrug'ini boshlash
@router.message(Command("calculate"))
async def start_calculation(message: types.Message, state: FSMContext):
    await message.answer("Kvadrat metr uchun narxni kiriting:")
    await state.set_state(PriceCalculation.price_per_m2)

# Kvadrat metr narxini qabul qilish
@router.message(PriceCalculation.price_per_m2)
async def set_price_per_m2(message: types.Message, state: FSMContext):
    price_per_m2 = float(message.text) * 1_000_000 if float(message.text) <= 9 else float(message.text)
    await state.update_data(price_per_m2=price_per_m2)
    await message.answer("Uyning maydonini kiriting (m²):")
    await state.set_state(PriceCalculation.area)

# Uyning maydonini qabul qilish
@router.message(PriceCalculation.area)
async def set_area(message: types.Message, state: FSMContext):
    await state.update_data(area=float(message.text))
    await message.answer("Xonalar sonini kiriting:")
    await state.set_state(PriceCalculation.rooms)

# Xonalar sonini qabul qilish
@router.message(PriceCalculation.rooms)
async def set_rooms(message: types.Message, state: FSMContext):
    await state.update_data(rooms=int(message.text))
    await message.answer("Nechinchi qavatda joylashganini kiriting:")
    await state.set_state(PriceCalculation.floor_level)

# Qavatni qabul qilish
@router.message(PriceCalculation.floor_level)
async def set_floor_level(message: types.Message, state: FSMContext):
    await state.update_data(floor_level=int(message.text))
    await message.answer("Boshlang'ich to'lov foizini kiriting:")
    await state.set_state(PriceCalculation.down_payment_percentage)

# Boshlang'ich to'lov foizini qabul qilish
@router.message(PriceCalculation.down_payment_percentage)
async def set_down_payment_percentage(message: types.Message, state: FSMContext):
    await state.update_data(down_payment_percentage=float(message.text))
    await message.answer("Bo'lib to'lash muddatini kiriting (oylarda):")
    await state.set_state(PriceCalculation.installment_months)

# Bo'lib to'lash muddatini qabul qilish
@router.message(PriceCalculation.installment_months)
async def set_installment_months(message: types.Message, state: FSMContext):
    await state.update_data(installment_months=int(message.text))
    await message.answer("Chegirma summasini kiriting:")
    await state.set_state(PriceCalculation.discount_amount)

# Chegirma summasini qabul qilish va natijani chiqarish
@router.message(PriceCalculation.discount_amount)
async def calculate_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    discount_amount = float(message.text) * 1_000_000
    
    # Hisoblash
    initial_price = data['price_per_m2'] * data['area']
    total_price = initial_price - discount_amount
    down_payment = total_price * (data['down_payment_percentage'] / 100)
    remaining_balance = total_price - down_payment
    monthly_payment = remaining_balance / data['installment_months']



    # Natijani foydalanuvchiga chiqarish
    response = (
        f"🏠 Strong Home kompaniyasi xonadoni hisoboti\n\n"
        f"✨ Uyning maydoni: {data['area']} m²\n"
        f"🛏️ Xonalar soni: {data['rooms']}\n"
        f"🏢 Nechinchi qavatda joylashgan: {data['floor_level']}-qavat\n\n"
        f"💲 Umumiy narx (chegirmasiz): {initial_price:,.2f} UZS\n"
    )

    if discount_amount > 0:
        response += (
            f"🎉 Chegirma: {discount_amount:,.2f} UZS\n"
        )

    response += (
        f"🔖 Chegirmadagi narx: {total_price:,.2f} UZS\n"
        f"💰 Boshlang'ich to'lov: {down_payment:,.2f} UZS\n"
        f"📅 Oyiga to'lov: {monthly_payment:,.2f} UZS ({data['installment_months']} oy davomida)\n\n"
        f"📞 Aloqa uchun:\n"
        f"+998982783003\n"
        f"+998553510047\n"
        f"+998553510074"
    )


    # Natijani foydalanuvchiga chiqarish
    await message.answer(response)



    await state.clear()

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
