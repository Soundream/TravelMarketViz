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

    // Animation settings
    animation: {
        duration: 1000,
        frameDelay: 1500,
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