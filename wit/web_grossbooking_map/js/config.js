const appConfig = {
    // Region colors based on representative flags
    regionColors: {
        'Asia-Pacific': '#DE2910',
        'Europe': '#003399',
        'Eastern Europe': '#4B0082',
        'Latin America': '#009B3A',
        'Middle East': '#8B4513',
        'North America': '#00BCD4'
    },

    // Color dictionary for countries
    colorDict: {
        'U.S.': '#00BCD4',
        'Canada': '#00BCD4',
        'Mexico': '#00BCD4',
        'Brazil': '#009B3A',
        'Argentina': '#009B3A',
        'Colombia': '#009B3A',
        'Chile': '#009B3A',
        'U.K.': '#003399',
        'France': '#003399',
        'Germany': '#003399',
        'Italy': '#003399',
        'Spain': '#003399',
        'Russia': '#4B0082',
        'China': '#DE2910',
        'Japan': '#DE2910',
        'South Korea': '#DE2910',
        'India': '#DE2910',
        'Australia-New Zealand': '#DE2910',
        'Singapore': '#DE2910',
        'Indonesia': '#DE2910',
        'Malaysia': '#DE2910',
        'Thailand': '#DE2910',
        'Taiwan': '#DE2910',
        'Hong Kong': '#DE2910'
    },

    // Animation settings
    animation: {
        duration: 500,
        frameDelay: 2000,
    },

    // Map settings
    map: {
        minBubbleSize: 10,
        maxBubbleSize: 80,
        defaultYear: 2005,
        projection: 'natural earth',
        hoverTemplate: '<b>%{hovertext}</b><br>' +
                      'Gross Bookings: $%{customdata[0]}B<br>' +
                      'Year: %{customdata[1]}'
    },

    // Data processing settings
    dataProcessing: {
        bookingsScaleFactor: 1e-9, // Convert to billions
        minValue: 0,
        maxValue: 1000
    },

    // Country codes mapping
    countryCodes: {
        'U.S.': 'USA',
        'Canada': 'CAN',
        'Mexico': 'MEX',
        'Brazil': 'BRA',
        'Argentina': 'ARG',
        'Colombia': 'COL',
        'Chile': 'CHL',
        'U.K.': 'GBR',
        'France': 'FRA',
        'Germany': 'DEU',
        'Italy': 'ITA',
        'Spain': 'ESP',
        'Russia': 'RUS',
        'China': 'CHN',
        'Japan': 'JPN',
        'South Korea': 'KOR',
        'India': 'IND',
        'Australia-New Zealand': 'AUS',
        'Singapore': 'SGP',
        'Indonesia': 'IDN',
        'Malaysia': 'MYS',
        'Thailand': 'THA',
        'Taiwan': 'TWN',
        'Hong Kong': 'HKG'
    },

    // Region definitions
    regions: {
        'North America': ['USA', 'CAN', 'MEX'],
        'Latin America': ['BRA', 'ARG', 'COL', 'CHL', 'PER', 'VEN', 'ECU', 'BOL', 'PRY', 'URY'],
        'Europe': ['GBR', 'FRA', 'DEU', 'ITA', 'ESP', 'NLD', 'CHE', 'BEL', 'PRT', 'IRL', 'DNK', 'NOR', 'SWE', 'FIN'],
        'Eastern Europe': ['RUS', 'POL', 'UKR', 'CZE', 'HUN', 'ROU', 'BGR', 'SVK', 'BLR', 'LTU', 'LVA', 'EST'],
        'Middle East': ['SAU', 'ARE', 'IRN', 'ISR', 'QAT', 'KWT', 'OMN', 'BHR', 'JOR', 'LBN'],
        'Asia-Pacific': ['CHN', 'JPN', 'KOR', 'AUS', 'IDN', 'IND', 'SGP', 'MYS', 'NZL', 'THA', 'VNM', 'PHL', 'TWN', 'HKG']
    }
}; 