class ValueChainResponse {
  final String theme;
  final Map<String, List<ValueChainItem>> usDrivers;

  ValueChainResponse({required this.theme, required this.usDrivers});

  factory ValueChainResponse.fromJson(Map<String, dynamic> json) {
    Map<String, List<ValueChainItem>> drivers = {};

    if (json['us_drivers'] != null) {
      Map<String, dynamic> drvMap = json['us_drivers'];
      drvMap.forEach((key, value) {
        if (value is List) {
          drivers[key] = value.map((e) => ValueChainItem.fromJson(e)).toList();
        }
      });
    }

    return ValueChainResponse(
      theme: json['theme'] ?? '',
      usDrivers: drivers,
    );
  }
}

class ValueChainItem {
  final String krStock;
  final String relation;
  final String description;

  ValueChainItem({
    required this.krStock,
    required this.relation,
    required this.description,
  });

  factory ValueChainItem.fromJson(Map<String, dynamic> json) {
    return ValueChainItem(
      krStock: json['kr_stock'] ?? '',
      relation: json['relation'] ?? '',
      description: json['description'] ?? '',
    );
  }
}
