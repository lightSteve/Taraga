# 🎨 Taraga UI Redesign Plan

## Design Inspiration

**Template:** [Animated App with Rive](https://www.flutterlibrary.com/templates/animated-app-with-rive)

## Key Design Elements

### 1. Color Palette

- **Background**: Dark theme (#0A0E27, #1A1F3A)
- **Accent Colors**:
  - Blue (#4A90E2) - US Market
  - Orange (#FF9500) - Retail/Burger
  - Red (#FF3B30) - Positive/Up
  - Cyan (#5AC8FA) - Institutional

### 2. Animation Strategy

- **Rive Animations**:
  - Loading states
  - Success/Error feedback
  - Bottom navigation icons
  - Background gradient animation
  
- **Flutter Animations**:
  - Card transitions
  - Page transitions
  - Shimmer effects

### 3. Insight Tab Redesign (3 Sections)

#### Section 1: Personal Matches (내 관심종목 인사이트)

- **Layout**: Horizontal PageView with auto-scroll
- **Card Design**:
  - Left: US ETF/Sector (Icon + Name + Change%)
  - Center: Arrow animation
  - Right: KR Stock (Name + Expected Flow)
- **Data Source**: `/api/v1/insight/personal-matches`

#### Section 2: Bridge News (브릿지 뉴스)

- **Layout**: Vertical ListView
- **Card Design**: Current implementation (US → KR)
- **Enhancement**: Add Rive loading animation
- **Data Source**: `/api/v1/insight/news-bridge`

#### Section 3: Value Chain (테마별 가치사슬)

- **Layout**: Expandable tree view
- **Interaction**: Tap theme → Show US drivers → Show KR stocks
- **Data Source**: `/api/v1/insight/value-chain?theme_id={id}`

### 4. Home Screen Enhancements

- **Background**: Animated gradient using Rive
- **Cards**: Add subtle shadow and elevation
- **Transitions**: Smooth page transitions

### 5. Bottom Navigation

- **Icons**: Rive animated icons
- **States**: Active/Inactive with smooth transitions

## Implementation Steps

1. ✅ Add Rive package to pubspec.yaml
2. ✅ Add UUID package for device-based auth
3. ✅ Create user UUID service
4. ✅ Redesign Insight Screen (3 sections)
5. ✅ Add Rive animations
6. ✅ Update bottom navigation with animated icons
7. ✅ Polish home screen with background animation

## Package Dependencies

```yaml
dependencies:
  rive: ^0.13.0
  uuid: ^4.0.0
  shared_preferences: ^2.2.0
```
