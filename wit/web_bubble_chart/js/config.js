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
    "Australia-New Zealand": "logos/Australia Icon.png"
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
    'Australia-New Zealand': '#00008b'
};

// Default selected companies - now including all countries
const defaultSelectedCompanies = [
    "Singapore", "China", "India", "Indonesia", "Malaysia", 
    "Thailand", "Vietnam", "Philippines", "Japan", "South Korea",
    "Hong Kong", "Taiwan", "Macau", "Australia-New Zealand"
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
    "Australia-New Zealand": "Australia-New Zealand"
};

// Export configurations
window.appConfig = {
    companyLogos,
    colorDict,
    defaultSelectedCompanies,
    companyNames
}; 