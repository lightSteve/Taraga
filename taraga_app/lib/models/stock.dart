/// Data model for stock information
class Stock {
  final String ticker;
  final String name;
  final String? sector;
  final int? themeId;
  final double? currentPrice;
  final double? changePercent;

  Stock({
    required this.ticker,
    required this.name,
    this.sector,
    this.themeId,
    this.currentPrice,
    this.changePercent,
  });

  factory Stock.fromJson(Map<String, dynamic> json) {
    return Stock(
      ticker: json['ticker'] as String,
      name: json['name'] as String,
      sector: json['sector'] as String?,
      themeId: json['theme_id'] as int?,
      currentPrice: json['current_price'] != null
          ? (json['current_price'] as num).toDouble()
          : null,
      changePercent: json['change_percent'] != null
          ? (json['change_percent'] as num).toDouble()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'ticker': ticker,
      'name': name,
      'sector': sector,
      'theme_id': themeId,
      'current_price': currentPrice,
      'change_percent': changePercent,
    };
  }
}
