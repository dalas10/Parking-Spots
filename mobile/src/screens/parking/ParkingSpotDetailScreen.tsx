import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
  Alert,
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { useParkingSpotStore, useBookingStore } from '../../stores';
import { ParkingSpot } from '../../types';

const { width } = Dimensions.get('window');

interface ParkingSpotDetailScreenProps {
  route: { params: { spotId: string } };
  navigation: any;
}

export const ParkingSpotDetailScreen: React.FC<ParkingSpotDetailScreenProps> = ({
  route,
  navigation,
}) => {
  const { spotId } = route.params;
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  const { selectedSpot, isLoadingSpot, getSpotDetails } = useParkingSpotStore();

  useEffect(() => {
    getSpotDetails(spotId);
  }, [spotId]);

  const formatPrice = (cents: number) => `€${(cents / 100).toFixed(2)}`;

  const handleBookNow = () => {
    navigation.navigate('BookingCreate', { spotId });
  };

  const handleViewReviews = () => {
    navigation.navigate('Reviews', { spotId });
  };

  if (isLoadingSpot || !selectedSpot) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  const spot = selectedSpot;

  return (
    <View style={styles.container}>
      <ScrollView>
        {/* Image carousel */}
        <View style={styles.imageContainer}>
          {spot.images && spot.images.length > 0 ? (
            <ScrollView
              horizontal
              pagingEnabled
              showsHorizontalScrollIndicator={false}
              onScroll={(e) => {
                const index = Math.round(e.nativeEvent.contentOffset.x / width);
                setCurrentImageIndex(index);
              }}
            >
              {spot.images.map((image, index) => (
                <Image
                  key={index}
                  source={{ uri: image }}
                  style={styles.image}
                  resizeMode="cover"
                />
              ))}
            </ScrollView>
          ) : (
            <View style={styles.noImage}>
              <Text style={styles.noImageText}>No images available</Text>
            </View>
          )}
          {spot.images && spot.images.length > 1 && (
            <View style={styles.pagination}>
              {spot.images.map((_, index) => (
                <View
                  key={index}
                  style={[
                    styles.paginationDot,
                    index === currentImageIndex && styles.paginationDotActive,
                  ]}
                />
              ))}
            </View>
          )}
        </View>

        <View style={styles.content}>
          {/* Title and rating */}
          <View style={styles.header}>
            <Text style={styles.title}>{spot.title}</Text>
            <TouchableOpacity
              style={styles.ratingBadge}
              onPress={handleViewReviews}
            >
              <Text style={styles.ratingText}>★ {spot.average_rating.toFixed(1)}</Text>
              <Text style={styles.reviewCount}>({spot.total_reviews} reviews)</Text>
            </TouchableOpacity>
          </View>

          {/* Address */}
          <Text style={styles.address}>
            {spot.address}, {spot.city}, {spot.prefecture} {spot.zip_code}
          </Text>

          {/* Pricing */}
          <View style={styles.pricingContainer}>
            <View style={styles.priceItem}>
              <Text style={styles.priceLabel}>Hourly</Text>
              <Text style={styles.priceValue}>{formatPrice(spot.hourly_rate)}</Text>
            </View>
            {spot.daily_rate && (
              <View style={styles.priceItem}>
                <Text style={styles.priceLabel}>Daily</Text>
                <Text style={styles.priceValue}>{formatPrice(spot.daily_rate)}</Text>
              </View>
            )}
            {spot.monthly_rate && (
              <View style={styles.priceItem}>
                <Text style={styles.priceLabel}>Monthly</Text>
                <Text style={styles.priceValue}>{formatPrice(spot.monthly_rate)}</Text>
              </View>
            )}
          </View>

          {/* Features */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Features</Text>
            <View style={styles.featuresGrid}>
              <FeatureItem
                label="Type"
                value={spot.spot_type.replace('_', ' ')}
                active
              />
              <FeatureItem
                label="Vehicle Size"
                value={spot.vehicle_size}
                active
              />
              <FeatureItem label="Covered" active={spot.is_covered} />
              <FeatureItem label="EV Charging" active={spot.has_ev_charging} />
              <FeatureItem label="Security" active={spot.has_security} />
              <FeatureItem label="Lighting" active={spot.has_lighting} />
              <FeatureItem label="Handicap Access" active={spot.is_handicap_accessible} />
            </View>
          </View>

          {/* Description */}
          {spot.description && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Description</Text>
              <Text style={styles.description}>{spot.description}</Text>
            </View>
          )}

          {/* Location map */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Location</Text>
            <View style={styles.mapContainer}>
              <MapView
                style={styles.map}
                scrollEnabled={false}
                zoomEnabled={false}
                initialRegion={{
                  latitude: spot.latitude,
                  longitude: spot.longitude,
                  latitudeDelta: 0.01,
                  longitudeDelta: 0.01,
                }}
              >
                <Marker
                  coordinate={{
                    latitude: spot.latitude,
                    longitude: spot.longitude,
                  }}
                  pinColor="#4F46E5"
                />
              </MapView>
            </View>
          </View>

          {/* Access instructions */}
          {spot.access_instructions && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Access Instructions</Text>
              <Text style={styles.description}>{spot.access_instructions}</Text>
            </View>
          )}
        </View>
      </ScrollView>

      {/* Book button */}
      <View style={styles.footer}>
        <View style={styles.footerPrice}>
          <Text style={styles.footerPriceLabel}>From</Text>
          <Text style={styles.footerPriceValue}>
            {formatPrice(spot.hourly_rate)}/hr
          </Text>
        </View>
        <TouchableOpacity
          style={[styles.bookButton, !spot.is_available && styles.bookButtonDisabled]}
          onPress={handleBookNow}
          disabled={!spot.is_available}
        >
          <Text style={styles.bookButtonText}>
            {spot.is_available ? 'Book Now' : 'Not Available'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

interface FeatureItemProps {
  label: string;
  value?: string;
  active: boolean;
}

const FeatureItem: React.FC<FeatureItemProps> = ({ label, value, active }) => (
  <View style={[styles.featureItem, active && styles.featureItemActive]}>
    <Text style={[styles.featureLabel, active && styles.featureLabelActive]}>
      {label}
    </Text>
    {value && (
      <Text style={[styles.featureValue, active && styles.featureValueActive]}>
        {value}
      </Text>
    )}
    {!value && (
      <Text style={[styles.featureCheck, active && styles.featureCheckActive]}>
        {active ? '✓' : '✗'}
      </Text>
    )}
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  imageContainer: {
    width,
    height: 250,
    backgroundColor: '#E5E7EB',
  },
  image: {
    width,
    height: 250,
  },
  noImage: {
    width,
    height: 250,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#E5E7EB',
  },
  noImageText: {
    color: '#9CA3AF',
  },
  pagination: {
    flexDirection: 'row',
    position: 'absolute',
    bottom: 16,
    alignSelf: 'center',
  },
  paginationDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(255,255,255,0.5)',
    marginHorizontal: 4,
  },
  paginationDotActive: {
    backgroundColor: '#fff',
  },
  content: {
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    flex: 1,
  },
  ratingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  ratingText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#D97706',
  },
  reviewCount: {
    fontSize: 12,
    color: '#D97706',
    marginLeft: 4,
  },
  address: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 16,
  },
  pricingContainer: {
    flexDirection: 'row',
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
  },
  priceItem: {
    flex: 1,
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  priceValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  featureItem: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    margin: 4,
    flexDirection: 'row',
    alignItems: 'center',
  },
  featureItemActive: {
    backgroundColor: '#EEF2FF',
  },
  featureLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  featureLabelActive: {
    color: '#4F46E5',
  },
  featureValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginLeft: 4,
    textTransform: 'capitalize',
  },
  featureValueActive: {
    color: '#4F46E5',
  },
  featureCheck: {
    fontSize: 14,
    marginLeft: 4,
    color: '#9CA3AF',
  },
  featureCheckActive: {
    color: '#10B981',
  },
  description: {
    fontSize: 16,
    color: '#4B5563',
    lineHeight: 24,
  },
  mapContainer: {
    height: 200,
    borderRadius: 12,
    overflow: 'hidden',
  },
  map: {
    flex: 1,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    backgroundColor: '#fff',
  },
  footerPrice: {
    flex: 1,
  },
  footerPriceLabel: {
    fontSize: 12,
    color: '#6B7280',
  },
  footerPriceValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
  },
  bookButton: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },
  bookButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  bookButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
