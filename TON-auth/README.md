# Инструкция по запуску TON NFT Auth

## Шаги для запуска

### 1. Установка зависимостей
Установите необходимые пакеты из `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
Перед запуском проекта создайте и заполните файл `.env`. Вы можете использовать файл `.env.example` как шаблон:

1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Откройте файл `.env` и заполните базовые переменные. Пример заполнения:

   ```env
   IS_TESTNET='True'
   TONCONNECT_MANIFEST_URL='https://storage.yandexcloud.net/kkotlyarenko-testing/tonconnect_manifest.json'
   TONCONNECT_KEY=''
   TONAPI_KEY='Your_tonapi_key'
   WALLET_MNEMONIC='Your_wallet_mnemonic'
   STORAGE_BUCKET='Your_storage_bucket'
   STORAGE_KEY='Your_storage_key'
   STORAGE_SECRET='Your_storage_secret'
   STORAGE_ENDPOINT='Your_storage_endpoint'
   ```

   **Примечания**:
   - Переменные `TONCONNECT_KEY` и `TONAPI_KEY` необязательны для тестирования и могут быть оставлены пустыми, но они необходимы для стабильной работы приложения.
   - Переменная `WALLET_MNEMONIC` должна содержать мнемонику кошелька из 24 слов, с которого будут выполняться транзакции.
   - Переменные `NFT_COLLECTION_ADDRESS` и `CIPHER_KEY` нужно будет заполнить вручную после первого запуска, когда они будут выведены в терминал.
   - Параметры `STORAGE_BUCKET`, `STORAGE_KEY`, `STORAGE_SECRET` и `STORAGE_ENDPOINT` относятся к настройке S3-хранилища, такого как Amazon S3 или Yandex Object Storage.

### 3. Первый запуск проекта
Запустите проект, выполнив следующую команду:

```bash
python main.py
```

При первом запуске программа:
- Проверит правильность введенной мнемоники кошелька.
- Предложит задеплоить NFT коллекцию.
- Сгенерирует адрес NFT коллекции и ключ шифрования (`CIPHER_KEY`), которые будут выведены в терминал.

### 4. Обновление `.env`
После успешного развертывания и первого запуска:

1. Вернитесь к файлу `.env`.
2. Добавьте сгенерированные значения:
   ```env
   NFT_COLLECTION_ADDRESS='Generated address from the first run'
   CIPHER_KEY='Generated key from the first run'
   ```

### 5. Перезапуск проекта
После обновления файла `.env` перезапустите проект:

```bash
python main.py
```

## Workflow использования

1. **Выбор кошелька для подключения**  
   После запуска программы вам будет предложено выбрать кошелек для подключения. Список доступных кошельков выглядит следующим образом:
   ```
   1. Wallet
   2. Tonkeeper
   3. MyTonWallet
   4. Tonhub
   5. DeWallet
   6. Bitget Wallet
   7. SafePal
   8. OKX Wallet
   9. OKX Mini Wallet
   10. HOT
   11. GateWallet
   12. Binance Web3 Wallet
   13. Fintopio
   ```
   Введите индекс кошелька, чтобы подключиться (например, для Tonkeeper: `2`).

2. **Подключение к кошельку**  
   Программа выведет QR-код и ссылку для подключения к кошельку. Отсканируйте QR-код с помощью выбранного кошелька или перейдите по ссылке для подтверждения подключения.

3. **Проверка наличия NFT**  
   Программа проверит наличие NFT на вашем кошельке. Если NFT отсутствует, будет предложено создать (mint) новый NFT:
   ```
   There is no nft on your wallet, do you want to mint one?
   Enter 'yes' or 'no':
   ```

   Введите `yes`, чтобы создать NFT.   

4. **Минтинг NFT**  
   Если вы согласились на создание NFT, программа выполнит mint и выведет индекс и адрес нового NFT:
   ```
   Successfully minted NFT with index 1: kQCtoUF1iQL3m0oq3s2-siVplc-sShyAuFemKAf_fm3j4TXm
   ```
    На Ваш кошелёк будет создана NFT содержащая в себе зашифрованный user_id который впоследствии будет использоваться для аутентификации.
5. **Вывод user_id (если NFT уже существует)**  
   В случае, если на вашем кошельке уже есть NFT, программа выведет соответствующий `user_id`.
   ```
   Authorized user id: 123456
   ```
---