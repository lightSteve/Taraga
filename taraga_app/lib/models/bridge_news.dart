class BridgeNews {
  final String usSource;
  final String usHeadline;
  final String krImpact;
  final List<RelatedStock> relatedStocks;
  final DateTime timestamp;

  BridgeNews({
    required this.usSource,
    required this.usHeadline,
    required this.krImpact,
    required this.relatedStocks,
    required this.timestamp,
  });

  factory BridgeNews.fromJson(Map<String, dynamic> json) {
    var rawStocks = json['related_stocks'] as List? ?? [];
    return BridgeNews(
      usSource: json['us_source'] ?? '',
      usHeadline: json['us_headline'] ?? '',
      krImpact: json['kr_impact'] ?? '',
      relatedStocks: rawStocks.map((s) => RelatedStock.fromJson(s)).toList(),
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}

class RelatedStock {
  final String name;
  final String ticker;
  final String change;

  RelatedStock({
    required this.name,
    required this.ticker,
    required this.change,
  });

  factory RelatedStock.fromJson(Map<String, dynamic> json) {
    return RelatedStock(
      name: json['name'] ?? '',
      ticker: json['ticker'] ?? '',
      change: json['change'] ?? '',
    );
  }
}
