Модель онлайн-аукциона (вариант 73)

Предметная область: интернет-торговля с использованием аукционных площадок.

Важные сущности: лот, участник аукциона, ставка, торговая площадка, таймер.

Операции: операция размещения лота, операция участия в торгах, операция управления ставками, операция завершения аукциона, операция оформления победы и платежей.

У класса TradingPlatform есть два состояния `preparing_for_auction`, `accepting_bids`, `auction_paused` возможные переходы 

```
        self.machine.add_transition(trigger='on_start_auction', source='preparing_for_auction', dest='accepting_bids')
        self.machine.add_transition(trigger='on_end_auction', source='accepting_bids', dest='preparing_for_auction')
        self.machine.add_transition(trigger='on_pause_auction', source='accepting_bids', dest='auction_paused')
        self.machine.add_transition(trigger='on_resume_auction', source='auction_paused', dest='accepting_bids')
        self.machine.add_transition(trigger='on_restart_auction', source='auction_paused', dest='accepting_bids')
        self.machine.add_transition(trigger='on_abort_auction', source='auction_paused', dest='preparing_for_auction')
```

Возможные действия во время каждого из состояний:
- `preparing_for_auction`:
  - добавление/удаление участника/лота
  - просмотр списка участников/лотов
  - смена баланса участника
  - смена времени таймера
- `accepting_new_bid`
  - принятие новой ставки (если не принято ни одной ставки до истечения таймера, то передача лота победителю аукциона и списание средств с победителя)

При запуске программы начальное состояние `preparing_for_auction`.

Сохранение состояния программы:
  - сохранение происходит автоматически при изменении значения атрибутов классов
  - если текущее состояние `preparing_for_auction`, то сохраняются значения всех классов
  - иначе (в состоянии `accepting_bids`) сохраняется состояние на момент до начала принятия ставок

## Основные сущности

