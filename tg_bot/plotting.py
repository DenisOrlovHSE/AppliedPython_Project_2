from typing import List
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO

from application.dto import WaterHistoryDTO, CalorieHistoryDTO


def plot_water_history(
    water_history: List[WaterHistoryDTO]
) -> bytes:
    plt.figure(figsize=(12, 6))

    sorted_history = sorted(water_history, key=lambda x: x.date_info)
    dates = [item.date_info for item in sorted_history]
    water_consumed = [item.water_consumed for item in sorted_history]

    bars = plt.bar(dates, water_consumed, label='Потреблено', color='#3498db', alpha=0.8, width=0.6)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9)
    
    plt.xlabel('Дата', fontsize=12, fontweight='bold')
    plt.ylabel('Вода (мл)', fontsize=12, fontweight='bold')
    plt.title('История потребления воды', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(True, alpha=0.3, axis='y')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, dpi=100, format='png')
    buf.seek(0)
    plt.close()
    
    return buf.getvalue()


def plot_calorie_history(
    calorie_history: List[CalorieHistoryDTO]
) -> bytes:
    plt.figure(figsize=(12, 6))

    sorted_history = sorted(calorie_history, key=lambda x: x.date_info)
    dates = [item.date_info for item in sorted_history]
    calories_consumed = [item.calories_consumed for item in sorted_history]
    calories_burned = [item.calories_burned for item in sorted_history]

    x = np.arange(len(dates))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, calories_consumed, width, label='Потреблено', color='#e74c3c', alpha=0.8)
    bars2 = plt.bar(x + width/2, calories_burned, width, label='Сожжено', color='#f39c12', alpha=0.8)

    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)
    
    plt.xlabel('Дата', fontsize=12, fontweight='bold')
    plt.ylabel('Калории (ккал)', fontsize=12, fontweight='bold')
    plt.title('История калорий', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(True, alpha=0.3, axis='y')

    date_labels = [d.strftime('%d.%m') for d in dates]
    plt.xticks(x, date_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, dpi=100, format='png')
    buf.seek(0)
    plt.close()
    
    return buf.getvalue()
