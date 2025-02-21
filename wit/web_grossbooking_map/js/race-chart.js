function createRaceChart(data, year) {
    console.log('\n=== Required Flags List ===');
    const allMarkets = [...new Set(data.map(d => d.Market))].sort();
    console.log('All markets in data:', allMarkets.join(', '));
    console.log('\nFlags needed:');
    allMarkets.forEach(market => {
        console.log(`'${market}': '${market} Icon.png',`);
    });
    console.log('=== End of Flags List ===\n');

    const flagMapping = {
        'Japan': 'Japan Icon.png',
        'China': 'China Icon.png',
        'Russia': 'Russia Icon.png',
        'Hong Kong': 'Hong Kong Icon.png',
        'U.K.': 'UK Icon.png',
        'Chile': 'Chile Icon.png',
        'U.S.': 'USA Icon.png',
        'Brazil': 'Brazil Icon.png',
        'Colombia': 'Colombia Icon.png',
        'Spain': 'Spain Icon.png',
        'Mexico': 'Mexico Icon.png',
        'Canada': 'Canada Icon.png',
        'U.A.E.': 'UAE Icon.png',
        'Australia-New Zealand': 'Australia Icon.png',
        'France': 'France Icon.png',
        'Germany': 'Germany Icon.png',
        'Italy': 'Italy Icon.png',
        'Rest of Europe': 'Europe Icon.png',
        'India': 'India Icon.png',
        'Scandinavia': 'Sweden Icon.png'
    };

    const maxValue = Math.max(...data.map(d => {
        return parseFloat(d['Gross Bookings']) || 0;
    }));

    window.globalMaxValue = maxValue;

    const yearData = data.filter(d => d.Year === year);

    const sortedData = yearData.map(d => {
        return {
            market: d.Market,
            value: parseFloat(d['Gross Bookings']) || 0,
            color: '#999999'
        };
    }).sort((a, b) => b.value - a.value).slice(0, 15);

    const barData = {
        type: 'bar',
        orientation: 'h',
        y: sortedData.map(d => d.market),
        x: sortedData.map(d => d.value),
        marker: {
            color: sortedData.map(d => d.color)
        },
        text: sortedData.map(d => d.value.toFixed(1)),
        textposition: 'outside',
        texttemplate: '%{text}B'
    };

    const layout = {
        width: 450,
        height: 400,
        xaxis: {
            range: [-1, maxValue * 1.6],
            fixedrange: true
        },
        yaxis: {
            showgrid: false,
            fixedrange: true,
            autorange: 'reversed'
        },
        margin: {
            l: 150,
            r: 200,
            t: 40,
            b: 50
        },
        showlegend: false
    };

    const config = {
        displayModeBar: false,
        responsive: true
    };

    Plotly.newPlot('race-chart', [barData], layout, config);
}

function updateRaceChart(data, year) {
    const yearData = data.filter(d => d.Year === year);
    
    const sortedData = yearData.map(d => {
        return {
            market: d.Market,
            value: parseFloat(d['Gross Bookings']) || 0,
            color: '#999999'
        };
    }).sort((a, b) => b.value - a.value).slice(0, 15);

    const updatedData = [{
        type: 'bar',
        orientation: 'h',
        y: sortedData.map(d => d.market),
        x: sortedData.map(d => d.value),
        marker: {
            color: sortedData.map(d => d.color)
        },
        text: sortedData.map(d => d.value.toFixed(1)),
        textposition: 'outside',
        texttemplate: '%{text}B'
    }];

    Plotly.react('race-chart', updatedData, {width: 450, height: 400});
}