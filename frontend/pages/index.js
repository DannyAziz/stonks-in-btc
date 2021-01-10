import Head from 'next/head'
import { useState } from 'react';
import useSWR from 'swr'
import styled from 'styled-components';
import { Reset } from 'styled-reset';
import Select from 'react-select'
import { format, sub, parseISO } from 'date-fns'
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

if (typeof Highcharts === 'object') {
  Highcharts.setOptions({
    chart: {
      style: {
        fontFamily: 'Helvetica Neue'
      }
    }
  })
}

const fetcher = (...args) => fetch(...args).then(res => res.json());
const API_URL = 'http://localhost:8000'

const Container = styled.div`
  background-color: #ECF0F1;
  min-height: 100vh;
  min-width: 100vw;

  font-family: "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif; 

  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 1fr 0.5fr 2.3fr 0.2fr;
  gap: 0px 0px;

  justify-items: center;
  align-items: center;
`;

const TitleSection = styled.section``;

const Title = styled.h1`
  display: flex;
  align-items: center;

  font-style: normal;
  font-weight: 500;
  font-size: 55px;
  line-height: 67px;
  text-align: center;

  @media only screen and (max-width: 480px)  {
    flex-direction: column;
    font-size: 40px;
  }

`;

const SelectContainer = styled.div`
  min-width: 250px;
  font-size: 45px;
  line-height: 55px;
  margin: 0 10px;

  @media only screen and (max-width: 480px)  {
    font-size: 35px;
  }
`;

const PriceSection = styled.section`
  align-self: flex-start;

  font-style: normal;
  font-weight: bold;
  font-size: 50px;
  line-height: 10px;

  @media only screen and (max-width: 480px)  {
    align-self: center;
  }
`;

const Price = styled.h1`
  color: ${p => p.gainer == 'gainer' ? 'green' : 'red'};
`;

const ChartSection = styled.section`
  width: 80%;

  @media only screen and (max-width: 480px)  {
    width: 100%;
  }
`;

const ChartSelectContainer = styled.div`
  width: 20%;
  margin-left: auto;
`;

const Footer = styled.footer``;

export default function Home() {
  const [stonk, setStonk] = useState({value: 11, label: '$TSLA'});
  const [period, setPeriod] = useState({value: '1y', label: '1y'})
  const { data: stonks, error: stonksError } = useSWR(`${API_URL}/stonks`, fetcher)
  const { data: currentPrice , error: currentPriceError } = useSWR(stonk ? `${API_URL}/stonks/${stonk.value}/price` : stonk, fetcher)

  const returnHistoricalUrl = () => {
    let baseURL = `${API_URL}/stonks/${stonk.value}/prices?start=`
    switch (period.value) {
      case '1w':
        return `${baseURL}${format(sub(new Date(), {weeks: 1}), 'yyyy-MM-dd')}&end=${format(new Date(), 'yyyy-MM-dd')}`
      case '1m':
        return `${baseURL}${format(sub(new Date(), {months: 1}), 'yyyy-MM-dd')}&end=${format(new Date(), 'yyyy-MM-dd')}`
      case '3m':
        return `${baseURL}${format(sub(new Date(), {months: 3}), 'yyyy-MM-dd')}&end=${format(new Date(), 'yyyy-MM-dd')}`
      case '1y':
        return `${baseURL}${format(sub(new Date(), {years: 1}), 'yyyy-MM-dd')}&end=${format(new Date(), 'yyyy-MM-dd')}`
      case '3y':
        return `${baseURL}${format(sub(new Date(), {years: 3}), 'yyyy-MM-dd')}&end=${format(new Date(), 'yyyy-MM-dd')}`
      case '5y':
        return `${baseURL}${format(sub(new Date(), {years: 5}), 'yyyy-MM-dd')}&end=${format(new Date(), 'yyyy-MM-dd')}`
      case 'all':
        return `${baseURL}2013-10-01&end=${format(new Date(), 'yyyy-MM-dd')}`
      default:
        return `${baseURL}${format(sub(new Date(), {years: 1}), 'yyyy-MM-dd')}&end=${format(new Date(), 'yyyy-MM-dd')}`
    }
  }

  const { data: historicalPrices , error: historicalPricesError } = useSWR(stonk ? returnHistoricalUrl() : stonk, fetcher)

  // if (currentPriceError) return <div>failed to load</div>
  // if (!currentPrice && stonk) return <div>loading...</div>

  const gainerOrLoser = () => {
    if (historicalPrices) {
      let firstPrice = historicalPrices[0].price;
      let lastPrice = historicalPrices[historicalPrices.length - 1].price;
      if (firstPrice < lastPrice) {
        return 'gainer'
      } else {
        return 'loser'
      }
    }
    return null;
  }

  const returnChartData = () => {
    if (historicalPrices) {
      return historicalPrices.map((item) => ({
        x: parseISO(item.datetime),
        y: item.price
      }))
    }
  }

  const options = {
    plotOptions: {
      line: {
        color: gainerOrLoser() == 'gainer' ? 'green' : 'red' 
      }
    },
    title: {
      text: undefined
    },
    credits: {
      enabled: false
    },
    exporting: {
      enabled: false
    },
    yAxis: {
      title: {
        text: undefined
      },
      labels: {
        format: 'BTC {value}'
      },
      gridLineWidth: 0
    },
    xAxis: {
      type: 'datetime',
      title: {
        text: undefined
      },
      tickLength: 0,
    },
    chart: {
      backgroundColor: 'transparent'
    },
    tooltip: {
      formatter: function () {
        return `
          <div>
            <span style='color: grey; font-size: 10px;'>${format(this.x, 'yyyy-MM-dd')}</span>
            <br />
            <span><b>BTC ${this.y.toFixed(5)}</b></span>
          </div>
        `
      }
    },
    series: [
      {
        data: returnChartData(),
        type: 'line',
        showInLegend: false,
        name: stonk.label,
        turboThreshold: 100000
      }
    ]
  }
  
  const returnStonkOptions = () => {
    if (stonks) {
      return stonks.map((item) => ({value: item.id, label: `$${item.ticker}`}))
    }
    return []
  }

  return (
    <Container>
      <Reset />
      <Head>
        <title>Stonks in BTC</title>
        <meta name="viewport" content="initial-scale=1.0, width=device-width" />
      </Head>
      <TitleSection>
        <Title>
          Price of
          <SelectContainer>
            <Select 
              options={returnStonkOptions()} 
              value={stonk}
              onChange={setStonk}
            />
          </SelectContainer>
          in BTC?
        </Title>
      </TitleSection>
      <PriceSection>
        {currentPrice &&
          <Price gainer={gainerOrLoser()}>BTC {currentPrice.price.toFixed(5)}</Price>
        }
      </PriceSection>
      <ChartSection>
        {historicalPrices &&
          <>
            <ChartSelectContainer>
              <Select 
                options={[
                  {value: '1w', label: '1w'},
                  {value: '1m', label: '1m'},
                  {value: '3m', label: '3m'},
                  {value: '1y', label: '1y'},
                  {value: '3y', label: '3y'},
                  {value: '5y', label: '5y'},
                  {value: 'all', label: 'all'}
                ]}
                isSearchable
                value={period}
                onChange={setPeriod}
              />
              </ChartSelectContainer>
            <>
              <HighchartsReact
                highcharts={Highcharts}
                options={options}
                // constructorType={"stockChart"}
              />
            </> 
          </>
        }
      </ChartSection>
      <Footer>
        Made with ☕ by <a target='_blank' href='https://twitter.com/dannyaziz97'>Danny Aziz</a>
      </Footer>
    </Container>
  )
}
