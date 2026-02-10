import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';
import { useParkingSpotStore } from '../../stores';
import { ParkingSpotListItem } from '../../types';

const { width, height } = Dimensions.get('window');

interface HomeScreenProps {
  navigation: any;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const mapRef = useRef<MapView>(null);
  const [showList, setShowList] = useState(false);
  const [selectedSpotId, setSelectedSpotId] = useState<string | null>(null);
  
  const {
    searchResults,
    isSearching,
    currentLocation,
    setCurrentLocation,
    searchNearby,
  } = useParkingSpotStore();

  useEffect(() => {
    requestLocationPermission();
  }, []);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const location = await Location.getCurrentPositionAsync({});
        const coords = {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
        };
        setCurrentLocation(coords);
        searchNearby(coords);
      }
    } catch (error) {
      console.error('Error getting location:', error);
    }
  };

  const handleMarkerPress = (spot: ParkingSpotListItem) => {
    setSelectedSpotId(spot.id);
  };

  const handleSpotPress = (spotId: string) => {
    navigation.navigate('ParkingSpotDetail', { spotId });
  };

  const formatPrice = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const renderSpotCard = ({ item }: { item: ParkingSpotListItem }) => (
    <TouchableOpacity
      style={[
        styles.spotCard,
        selectedSpotId === item.id && styles.spotCardSelected,
      ]}
      onPress={() => handleSpotPress(item.id)}
    >
      <View style={styles.spotCardContent}>
        <Text style={styles.spotTitle} numberOfLines={1}>
          {item.title}
        </Text>
        <Text style={styles.spotAddress} numberOfLines={1}>
          {item.address}, {item.city}
        </Text>
        <View style={styles.spotFooter}>
          <Text style={styles.spotPrice}>
            {formatPrice(item.hourly_rate)}/hr
          </Text>
          <View style={styles.ratingContainer}>
            <Text style={styles.ratingText}>★ {item.average_rating.toFixed(1)}</Text>
            <Text style={styles.reviewCount}>({item.total_reviews})</Text>
          </View>
        </View>
        {item.distance_km && (
          <Text style={styles.distance}>{item.distance_km.toFixed(1)} km away</Text>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <MapView
        ref={mapRef}
        style={styles.map}
        provider={PROVIDER_GOOGLE}
        showsUserLocation
        showsMyLocationButton
        initialRegion={
          currentLocation
            ? {
                ...currentLocation,
                latitudeDelta: 0.05,
                longitudeDelta: 0.05,
              }
            : {
                latitude: 40.7128,
                longitude: -74.006,
                latitudeDelta: 0.1,
                longitudeDelta: 0.1,
              }
        }
      >
        {searchResults.map((spot) => (
          <Marker
            key={spot.id}
            coordinate={{
              latitude: spot.latitude,
              longitude: spot.longitude,
            }}
            title={spot.title}
            description={`${formatPrice(spot.hourly_rate)}/hr`}
            onPress={() => handleMarkerPress(spot)}
            pinColor={selectedSpotId === spot.id ? '#4F46E5' : '#EF4444'}
          />
        ))}
      </MapView>

      {/* Search bar */}
      <View style={styles.searchContainer}>
        <TouchableOpacity
          style={styles.searchBar}
          onPress={() => navigation.navigate('Search')}
        >
          <Text style={styles.searchPlaceholder}>Search for parking...</Text>
        </TouchableOpacity>
      </View>

      {/* Toggle view button */}
      <TouchableOpacity
        style={styles.toggleButton}
        onPress={() => setShowList(!showList)}
      >
        <Text style={styles.toggleButtonText}>
          {showList ? 'Map View' : 'List View'}
        </Text>
      </TouchableOpacity>

      {/* Results list */}
      {isSearching ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4F46E5" />
        </View>
      ) : (
        <View style={[styles.listContainer, showList && styles.listContainerExpanded]}>
          <FlatList
            data={searchResults}
            renderItem={renderSpotCard}
            keyExtractor={(item) => item.id}
            horizontal={!showList}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={
              showList ? styles.verticalList : styles.horizontalList
            }
            ListEmptyComponent={
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>
                  No parking spots found nearby
                </Text>
              </View>
            }
          />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    width,
    height,
  },
  searchContainer: {
    position: 'absolute',
    top: 60,
    left: 16,
    right: 16,
  },
  searchBar: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  searchPlaceholder: {
    color: '#9CA3AF',
    fontSize: 16,
  },
  toggleButton: {
    position: 'absolute',
    top: 130,
    right: 16,
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  toggleButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  loadingContainer: {
    position: 'absolute',
    bottom: 100,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  listContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'transparent',
  },
  listContainerExpanded: {
    top: 180,
    backgroundColor: '#fff',
  },
  horizontalList: {
    paddingHorizontal: 16,
    paddingBottom: 100,
  },
  verticalList: {
    padding: 16,
  },
  spotCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginRight: 12,
    width: 280,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  spotCardSelected: {
    borderColor: '#4F46E5',
    borderWidth: 2,
  },
  spotCardContent: {},
  spotTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4,
  },
  spotAddress: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  spotFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  spotPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4F46E5',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    fontSize: 14,
    color: '#F59E0B',
    fontWeight: '600',
  },
  reviewCount: {
    fontSize: 12,
    color: '#9CA3AF',
    marginLeft: 4,
  },
  distance: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4,
  },
  emptyContainer: {
    padding: 24,
    alignItems: 'center',
  },
  emptyText: {
    color: '#6B7280',
    fontSize: 14,
  },
});
