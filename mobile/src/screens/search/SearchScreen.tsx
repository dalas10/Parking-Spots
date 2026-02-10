import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Switch,
  Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { Picker } from '@react-native-picker/picker';
import { useParkingSpotStore } from '../../stores';

interface SearchScreenProps {
  navigation: any;
}

export const SearchScreen: React.FC<SearchScreenProps> = ({ navigation }) => {
  const { searchNearby, setSearchFilters, currentLocation } = useParkingSpotStore();
  
  // Search state
  const [searchText, setSearchText] = useState('');
  const [city, setCity] = useState('');
  const [spotType, setSpotType] = useState<string>('');
  const [hasEVCharging, setHasEVCharging] = useState(false);
  const [isCovered, setIsCovered] = useState(false);
  
  // Date/Time state
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [showStartDatePicker, setShowStartDatePicker] = useState(false);
  const [showEndDatePicker, setShowEndDatePicker] = useState(false);
  const [useDateTime, setUseDateTime] = useState(false);
  
  const handleSearch = async () => {
    const params: any = {};
    
    // Text search
    if (searchText.trim()) {
      params.q = searchText.trim();
    }
    
    // City filter
    if (city.trim()) {
      params.city = city.trim();
    }
    
    // Spot type filter
    if (spotType) {
      params.spot_type = spotType;
    }
    
    // Boolean filters
    if (hasEVCharging) {
      params.has_ev_charging = true;
    }
    if (isCovered) {
      params.is_covered = true;
    }
    
    // Date/time filters
    if (useDateTime) {
      params.start_time = startDate.toISOString();
      params.end_time = endDate.toISOString();
    }
    
    // Location (use current if available)
    if (currentLocation) {
      params.latitude = currentLocation.latitude;
      params.longitude = currentLocation.longitude;
      params.radius_km = 50; // 50km radius
    }
    
    // Update filters and search
    setSearchFilters(params);
    await searchNearby(params);
    
    // Navigate back to map with results
    navigation.goBack();
  };
  
  const handleClearFilters = () => {
    setSearchText('');
    setCity('');
    setSpotType('');
    setHasEVCharging(false);
    setIsCovered(false);
    setUseDateTime(false);
    setStartDate(new Date());
    setEndDate(new Date());
  };
  
  const formatDateTime = (date: Date) => {
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };
  
  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Search Box */}
        <View style={styles.section}>
          <Text style={styles.label}>Search</Text>
          <TextInput
            style={styles.input}
            placeholder="Search by location, address..."
            value={searchText}
            onChangeText={setSearchText}
            autoCapitalize="words"
          />
        </View>
        
        {/* City Filter */}
        <View style={styles.section}>
          <Text style={styles.label}>City</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter city name"
            value={city}
            onChangeText={setCity}
            autoCapitalize="words"
          />
        </View>
        
        {/* Spot Type Filter */}
        <View style={styles.section}>
          <Text style={styles.label}>Parking Type</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={spotType}
              onValueChange={(value) => setSpotType(value)}
              style={styles.picker}
            >
              <Picker.Item label="All Types" value="" />
              <Picker.Item label="Indoor" value="indoor" />
              <Picker.Item label="Outdoor" value="outdoor" />
              <Picker.Item label="Covered" value="covered" />
              <Picker.Item label="Garage" value="garage" />
              <Picker.Item label="Driveway" value="driveway" />
              <Picker.Item label="Lot" value="lot" />
            </Picker>
          </View>
        </View>
        
        {/* Date/Time Section */}
        <View style={styles.section}>
          <View style={styles.switchRow}>
            <Text style={styles.label}>Filter by Date/Time</Text>
            <Switch
              value={useDateTime}
              onValueChange={setUseDateTime}
              trackColor={{ false: '#D1D5DB', true: '#FDB82E' }}
              thumbColor={useDateTime ? '#fff' : '#fff'}
            />
          </View>
          
          {useDateTime && (
            <View style={styles.dateTimeContainer}>
              {/* Start Date/Time */}
              <View style={styles.dateTimeRow}>
                <Text style={styles.dateLabel}>Start:</Text>
                <TouchableOpacity
                  style={styles.dateButton}
                  onPress={() => setShowStartDatePicker(true)}
                >
                  <Text style={styles.dateButtonText}>
                    {formatDateTime(startDate)}
                  </Text>
                </TouchableOpacity>
              </View>
              
              {showStartDatePicker && (
                <DateTimePicker
                  value={startDate}
                  mode="datetime"
                  display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                  onChange={(event, selectedDate) => {
                    setShowStartDatePicker(Platform.OS === 'ios');
                    if (selectedDate) {
                      setStartDate(selectedDate);
                      if (selectedDate > endDate) {
                        setEndDate(selectedDate);
                      }
                    }
                  }}
                />
              )}
              
              {/* End Date/Time */}
              <View style={styles.dateTimeRow}>
                <Text style={styles.dateLabel}>End:</Text>
                <TouchableOpacity
                  style={styles.dateButton}
                  onPress={() => setShowEndDatePicker(true)}
                >
                  <Text style={styles.dateButtonText}>
                    {formatDateTime(endDate)}
                  </Text>
                </TouchableOpacity>
              </View>
              
              {showEndDatePicker && (
                <DateTimePicker
                  value={endDate}
                  mode="datetime"
                  display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                  minimumDate={startDate}
                  onChange={(event, selectedDate) => {
                    setShowEndDatePicker(Platform.OS === 'ios');
                    if (selectedDate) {
                      setEndDate(selectedDate);
                    }
                  }}
                />
              )}
            </View>
          )}
        </View>
        
        {/* Amenities */}
        <View style={styles.section}>
          <Text style={styles.label}>Amenities</Text>
          
          <View style={styles.switchRow}>
            <Text style={styles.switchLabel}>EV Charging</Text>
            <Switch
              value={hasEVCharging}
              onValueChange={setHasEVCharging}
              trackColor={{ false: '#D1D5DB', true: '#FDB82E' }}
              thumbColor={hasEVCharging ? '#fff' : '#fff'}
            />
          </View>
          
          <View style={styles.switchRow}>
            <Text style={styles.switchLabel}>Covered Parking</Text>
            <Switch
              value={isCovered}
              onValueChange={setIsCovered}
              trackColor={{ false: '#D1D5DB', true: '#FDB82E' }}
              thumbColor={isCovered ? '#fff' : '#fff'}
            />
          </View>
        </View>
        
        {/* Action Buttons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.clearButton}
            onPress={handleClearFilters}
          >
            <Text style={styles.clearButtonText}>Clear Filters</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.searchButton}
            onPress={handleSearch}
          >
            <Text style={styles.searchButtonText}>Search</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#111827',
  },
  pickerContainer: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  switchLabel: {
    fontSize: 16,
    color: '#374151',
  },
  dateTimeContainer: {
    marginTop: 12,
  },
  dateTimeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  dateLabel: {
    fontSize: 16,
    color: '#374151',
    width: 60,
  },
  dateButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    padding: 12,
  },
  dateButtonText: {
    fontSize: 16,
    color: '#111827',
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 24,
    marginBottom: 40,
  },
  clearButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  clearButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  searchButton: {
    flex: 1,
    backgroundColor: '#FDB82E',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  searchButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});
