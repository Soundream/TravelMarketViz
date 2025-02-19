// Company logos mapping
const companyLogos = {
    "Singapore": "logos/Singapore Flag Icon.png",
    "China": "logos/China Flag Icon.png",
    "India": "logos/India Icon.png",
    "Indonesia": "logos/Indonesia Flag.png",
    "Malaysia": "logos/Malaysia Icon.png",
    "Thailand": "logos/Thailand Icon.png",
    "Vietnam": "logos/China Flag Icon.png",
    "Philippines": "logos/Singapore Flag Icon.png",
    "Japan": "logos/Japan Icon.png",
    "South Korea": "logos/Korea Icon.png",
    "Hong Kong": "logos/Hong Kong Icon.png",
    "Taiwan": "logos/Taiwan Icon.png",
    "Macau": "logos/Macau Icon.png",
    "Australia & New Zealand": "logos/Australia Icon.png"
};

// Color dictionary for companies
const colorDict = {
    'Singapore': '#ff5895',
    'China': '#003480',
    'India': '#ff9933',
    'Indonesia': '#ff0000',
    'Malaysia': '#cc0001',
    'Thailand': '#00247d',
    'Vietnam': '#da251d',
    'Philippines': '#0038a8',
    'Japan': '#bc002d',
    'South Korea': '#cd2e3a',
    'Hong Kong': '#de2910',
    'Taiwan': '#fe0000',
    'Macau': '#00785e',
    'Australia & New Zealand': '#00008b'
};

// Default selected companies - now including all countries
const defaultSelectedCompanies = [
    "Singapore", "China", "India", "Indonesia", "Malaysia", 
    "Thailand", "Vietnam", "Philippines", "Japan", "South Korea",
    "Hong Kong", "Taiwan", "Macau", "Australia & New Zealand"
];

// Company full names mapping
const companyNames = {
    "Singapore": "Singapore",
    "China": "China",
    "India": "India",
    "Indonesia": "Indonesia",
    "Malaysia": "Malaysia",
    "Thailand": "Thailand",
    "Vietnam": "Vietnam",
    "Philippines": "Philippines",
    "Japan": "Japan",
    "South Korea": "South Korea",
    "Hong Kong": "Hong Kong",
    "Taiwan": "Taiwan",
    "Macau": "Macau",
    "Australia & New Zealand": "Australia & New Zealand"
};

// Export configurations
const appConfig = {
    // Default selected companies for the bubble chart
    defaultSelectedCompanies: [
        'China',
        'Japan',
        'South Korea',
        'Australia & New Zealand',
        'India',
        'Indonesia',
        'Singapore',
        'Malaysia',
        'Thailand',
        'Vietnam',
        'Philippines',
        'Hong Kong',
        'Taiwan',
        'Macau'
    ],

    // Company logos for bubbles
    companyLogos: {
        "Singapore": "logos/Singapore Flag Icon.png",
        "China": "logos/China Flag Icon.png",
        "India": "logos/India Icon.png",
        "Indonesia": "logos/Indonesia Flag.png",
        "Malaysia": "logos/Malaysia Icon.png",
        "Thailand": "logos/Thailand Icon.png",
        "Vietnam": "logos/China Flag Icon.png",
        "Philippines": "logos/Singapore Flag Icon.png",
        "Japan": "logos/Japan Icon.png",
        "South Korea": "logos/Korea Icon.png",
        "Hong Kong": "logos/Hong Kong Icon.png",
        "Taiwan": "logos/Taiwan Icon.png",
        "Macau": "logos/Macau Icon.png",
        "Australia & New Zealand": "logos/Australia Icon.png"
    },

    // Color dictionary for companies
    colorDict: {
        'Singapore': '#ff5895',
        'China': '#003480',
        'India': '#ff9933',
        'Indonesia': '#ff0000',
        'Malaysia': '#cc0001',
        'Thailand': '#00247d',
        'Vietnam': '#da251d',
        'Philippines': '#0038a8',
        'Japan': '#bc002d',
        'South Korea': '#cd2e3a',
        'Hong Kong': '#de2910',
        'Taiwan': '#fe0000',
        'Macau': '#00785e',
        'Australia & New Zealand': '#00008b'
    },

    // Animation settings
    animation: {
        duration: 800,
        frameDelay: 1200,
    },

    // Chart settings
    chart: {
        minBubbleSize: 15,
        maxBubbleSize: 80,
        defaultYear: 2005,
        xAxisTitle: 'Online Penetration',
        yAxisTitle: 'Online Bookings Volume (Billion USD)',
    },

    // Data processing
    dataProcessing: {
        onlinePenetrationMultiplier: 100,
        bookingsScaleFactor: 1e-9,
        roundDecimals: 2
    },

    companyNames
}; 