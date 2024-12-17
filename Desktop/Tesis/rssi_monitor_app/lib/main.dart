import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:location/location.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RSSI Monitor',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final String videoFeedUrl = "https://localizador-por-triangulaci-n.onrender.com/video_feed";

  // ignore: non_constant_identifier_names
  List<String> areas_Higinio = [
    "Patio Trasero",
    "Cocina",
    "Patio Central",
    "Habitación Celina",
    "Habitación Higinio",
    "Habitación Nelson",
    "Pasillo",
    "Palco"
  ];

  // ignore: non_constant_identifier_names
  List<String> areas_Celina = [
    "Patio Trasero",
    "Cocina",
    "Patio Central",
    "Habitación Celina",
    "Habitación Higinio",
    "Habitación Nelson",
    "Pasillo",
    "Palco"
  ];

  String rssi1 = "Esperando datos...";
  String rssi2 = "Esperando datos...";
  String position = "Esperando datos...";
  // ignore: non_constant_identifier_names
  String area_Higinio = "Esperando datos...";
  // ignore: non_constant_identifier_names
  String area_Celina = "Esperando datos...";
  String cameraStatus = "Cámara: Activa";
  String esp32Status = "ESP32: Activo";

  final LatLng targetLocation = const LatLng(-0.257991, -78.537088);
  final double proximityThreshold = 0.001;

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  Future<void> fetchData() async {
    Random random = Random();

    while (true) {
      // Simulate RSSI values
      List<int> simulatedRssi = List.generate(5, (index) => random.nextInt(100));

      // Get the current location
      LatLng currentLocation = await getCurrentLocation();

      // Determine area based on simulated RSSI
      String simulatedAreaH = areas_Higinio[random.nextInt(areas_Higinio.length)];

      // Determine area for Celina based on location
      String simulatedAreaC = isNearby(currentLocation) ? "Cocina" : areas_Celina[random.nextInt(areas_Celina.length)];

      // Update state with simulated data
      setState(() {
        rssi1 = 'Punto Triangulación Higinio: ${simulatedRssi[0]}';
        rssi2 = 'Punto triangulación Celina: ${simulatedRssi[1]}';
        position = 'Position: (${(random.nextDouble() * 100).toStringAsFixed(2)}, ${(random.nextDouble() * 100).toStringAsFixed(2)})';
        area_Higinio = 'Área Higinio: $simulatedAreaH';
        area_Celina = 'Área Celina: $simulatedAreaC';
        cameraStatus = 'Cámara: Activa';
        esp32Status = 'ESP32: Activo';
      });

      await _saveData();
      await Future.delayed(const Duration(minutes: 7));
    }
  }

  Future<LatLng> getCurrentLocation() async {
    Location location = Location();
    LocationData? locationData = await location.getLocation();

    return LatLng(locationData.latitude!, locationData.longitude!);
    }

  bool isNearby(LatLng currentLocation) {
    double distance = _calculateDistance(currentLocation, targetLocation);
    return distance < proximityThreshold;
  }

  double _calculateDistance(LatLng location1, LatLng location2) {
    const double earthRadius = 6371.0; // Radio de la Tierra en kilómetros

    double lat1 = location1.latitude;
    double lon1 = location1.longitude;
    double lat2 = location2.latitude;
    double lon2 = location2.longitude;

    double dLat = _toRadians(lat2 - lat1);
    double dLon = _toRadians(lon2 - lon1);

    double a = sin(dLat / 2) * sin(dLat / 2) +
               cos(_toRadians(lat1)) * cos(_toRadians(lat2)) *
               sin(dLon / 2) * sin(dLon / 2);

    double c = 2 * atan2(sqrt(a), sqrt(1 - a));

    return earthRadius * c;
  }

  double _toRadians(double degrees) {
    return degrees * (pi / 180);
  }

  Future<void> _saveData() async {
    // Save the current state data using shared_preferences or another method
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('RSSI Monitor'),
      ),
      body: Column(
        children: <Widget>[
          Expanded(
            child: CachedNetworkImage(
              imageUrl: videoFeedUrl,
              placeholder: (context, url) => const Center(child: CircularProgressIndicator()),
              errorWidget: (context, url, error) => const Icon(Icons.error),
              fit: BoxFit.cover,
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16.0),
              children: <Widget>[
                Text(rssi1, style: const TextStyle(fontSize: 18)),
                Text(rssi2, style: const TextStyle(fontSize: 18)),
                Text(position, style: const TextStyle(fontSize: 18)),
                Text(area_Higinio, style: const TextStyle(fontSize: 18)),
                Text(area_Celina, style: const TextStyle(fontSize: 18)),
                Text(cameraStatus, style: const TextStyle(fontSize: 18)),
                Text(esp32Status, style: const TextStyle(fontSize: 18)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
