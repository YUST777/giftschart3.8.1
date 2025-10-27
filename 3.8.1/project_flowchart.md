# Telegram Gift Price Bot - Project Flowchart

```mermaid
graph TB
    %% User Interactions
    User[👤 User] --> Bot[🤖 Telegram Bot]
    User --> InlineQuery[📱 Inline Query]
    User --> Commands[⌨️ Commands]
    
    %% Main Bot Entry Points
    Bot --> MainBot[telegram_bot.py]
    InlineQuery --> InlineHandler[Inline Query Handler]
    Commands --> CommandHandler[Command Handler]
    
    %% Command Types
    CommandHandler --> StartCmd[/start]
    CommandHandler --> HelpCmd[/help]
    CommandHandler --> PremiumCmd[/premium]
    CommandHandler --> StickerCmd[/sticker]
    CommandHandler --> AdminCmd[/admin]
    
    %% Message Processing
    MainBot --> MessageHandler[Message Handler]
    MessageHandler --> GiftSearch[Gift Name Search]
    MessageHandler --> StickerSearch[Sticker Search]
    
    %% Gift Processing Flow
    GiftSearch --> FindGifts[Find Matching Gifts]
    FindGifts --> SingleGift{Single Gift?}
    SingleGift -->|Yes| SendGiftCard[Send Gift Card]
    SingleGift -->|No| ShowGiftList[Show Gift List]
    
    %% Gift Card Generation
    SendGiftCard --> GenerateCard[Generate Gift Card]
    GenerateCard --> NewCardDesign[new_card_design.py]
    
    %% API Integration
    NewCardDesign --> CheckGiftType{Gift Type?}
    CheckGiftType -->|Premarket| TonnelAPI[🌉 Tonnel API]
    CheckGiftType -->|Regular| PortalAPI[🚪 Portal API]
    
    %% API Details
    TonnelAPI --> TonnelModule[tonnel_api.py]
    PortalAPI --> PortalModule[portal_api.py]
    
    %% Data Sources
    TonnelModule --> TonnelData[Real Premarket Prices]
    PortalModule --> PortalData[Real Regular Prices]
    PortalModule --> MockData[Mock Data for New Gifts]
    
    %% Chart Data
    NewCardDesign --> ChartData[Chart Data]
    ChartData --> TonnelChart[Legacy API Charts]
    ChartData --> PortalChart[Portal API Charts]
    
    %% Card Components
    NewCardDesign --> CardComponents[Card Components]
    CardComponents --> GiftImage[Gift Image]
    CardComponents --> PriceDisplay[Price Display]
    CardComponents --> ChartImage[Chart Image]
    CardComponents --> SupplyBadge[Supply Badge]
    CardComponents --> Watermark[Watermark]
    
    %% Image Sources
    GiftImage --> DownloadedImages[downloaded_images/]
    CardComponents --> GeneratedCards[new_gift_cards/]
    
    %% Sticker System
    StickerSearch --> StickerIntegration[sticker_integration.py]
    StickerIntegration --> StickerCollections[sticker_collections/]
    StickerIntegration --> StickerCards[Sticker Price Cards]
    
    %% Premium System
    PremiumCmd --> PremiumSystem[premium_system.py]
    PremiumSystem --> PaymentProcessing[Payment Processing]
    PremiumSystem --> GroupManagement[Group Management]
    PremiumSystem --> LinkConfiguration[Link Configuration]
    
    %% Database Layer
    MainBot --> Database[(SQLite Database)]
    Database --> RateLimiter[rate_limiter.py]
    Database --> BotConfig[bot_config.py]
    Database --> AdminDashboard[admin_dashboard.py]
    
    %% Background Services
    MainBot --> BackgroundServices[Background Services]
    BackgroundServices --> CardPregeneration[pregenerate_gift_cards.py]
    BackgroundServices --> BackupSystem[backup_scheduler.py]
    BackgroundServices --> PriceUpdates[Price Update Schedulers]
    
    %% Card Pregeneration
    CardPregeneration --> ScheduleCards[Schedule Card Generation]
    ScheduleCards --> GenerateAllCards[Generate All Cards]
    GenerateAllCards --> NewCardDesign
    
    %% Backup System
    BackupSystem --> DatabaseBackup[Database Backup]
    DatabaseBackup --> ZipBackup[Create ZIP Backup]
    ZipBackup --> SendToAdmins[Send to Admin Group]
    
    %% Price Update System
    PriceUpdates --> StickerPriceUpdate[sticker_price_update_and_cardgen.py]
    PriceUpdates --> PremarketScheduler[premarket_scheduler.py]
    
    %% Configuration Files
    BotConfig --> Config[Configuration]
    Config --> BotToken[Bot Token]
    Config --> AdminUsers[Admin Users]
    Config --> SpecialGroups[Special Groups]
    Config --> GiftNames[Gift Names List]
    
    %% File Structure
    DownloadedImages --> ImageFiles[PNG Image Files]
    GeneratedCards --> CardFiles[Generated Card Files]
    StickerCollections --> StickerFiles[Sticker Collection Files]
    
    %% API Endpoints
    TonnelAPI --> TonnelEndpoints[Legacy API Endpoints]
    PortalAPI --> PortalEndpoints[Portal API Endpoints]
    PortalEndpoints --> AuthToken[Authentication Token]
    
    %% Error Handling
    MainBot --> ErrorHandling[Error Handling]
    ErrorHandling --> Logging[Logging System]
    ErrorHandling --> FallbackData[Fallback Data]
    
    %% Rate Limiting
    MessageHandler --> RateLimitCheck[Rate Limit Check]
    RateLimitCheck --> AllowRequest[Allow Request]
    RateLimitCheck --> BlockRequest[Block Request]
    
    %% Admin Features
    AdminCmd --> AdminDashboard
    AdminDashboard --> Analytics[Analytics Dashboard]
    AdminDashboard --> UserStats[User Statistics]
    AdminDashboard --> SystemStatus[System Status]
    
    %% Styling
    classDef userClass fill:#e1f5fe
    classDef botClass fill:#f3e5f5
    classDef apiClass fill:#e8f5e8
    classDef dataClass fill:#fff3e0
    classDef fileClass fill:#fce4ec
    classDef serviceClass fill:#f1f8e9
    
    class User userClass
    class Bot,MainBot,MessageHandler botClass
    class TonnelAPI,PortalAPI,TonnelModule,PortalModule apiClass
    class Database,Config,RateLimiter dataClass
    class DownloadedImages,GeneratedCards,StickerCollections fileClass
    class BackgroundServices,CardPregeneration,BackupSystem serviceClass
```

## Key Components:

### 🤖 **Core Bot System**
- **telegram_bot.py**: Main bot logic and message handling
- **bot_config.py**: Configuration and database management
- **rate_limiter.py**: Rate limiting and user management

### 🌐 **API Integration**
- **Tonnel API**: Real prices for premarket gifts
- **Portal API**: Real prices for regular gifts + mock data for new gifts
- **Legacy API**: Chart data and supply information

### 🎨 **Card Generation**
- **new_card_design.py**: Dynamic gift card generation
- **downloaded_images/**: Source gift images
- **new_gift_cards/**: Generated price cards

### 🏷️ **Sticker System**
- **sticker_integration.py**: Sticker collection management
- **sticker_collections/**: Sticker collection data
- **Sticker Price Cards**: Dynamic sticker pricing

### 💎 **Premium System**
- **premium_system.py**: Payment processing and group management
- **Link Configuration**: Referral link management
- **Group Management**: Premium group features

### 🔄 **Background Services**
- **Card Pregeneration**: Scheduled card generation
- **Backup System**: Automated database backups
- **Price Updates**: Real-time price monitoring

### 📊 **Admin Features**
- **admin_dashboard.py**: Analytics and system monitoring
- **User Statistics**: Usage analytics
- **System Status**: Health monitoring
