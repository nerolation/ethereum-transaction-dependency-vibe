import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import GraphViewer from './components/GraphViewer';
import GanttViewer from './components/GanttViewer';
import GraphSearch from './components/GraphSearch';
import RecentGraphs from './components/RecentGraphs';
import ViewToggle, { ViewType } from './components/ViewToggle';
import { GlobalStyle } from './styles/GlobalStyle';
import api from './api';

const AppContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 60px); /* Subtract footer height */
`;

const Header = styled.header`
  margin-bottom: 2rem;
  text-align: center;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: #7f8c8d;
`;

const Main = styled.main`
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
`;

const DemoBanner = styled.div`
  background-color: #f39c12;
  color: white;
  text-align: center;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  font-weight: 500;
`;

const StatusIndicator = styled.div<{ isConnected: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  color: ${props => props.isConnected ? '#27ae60' : '#e74c3c'};
`;

const StatusDot = styled.div<{ isConnected: boolean }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => props.isConnected ? '#27ae60' : '#e74c3c'};
`;

const Footer = styled.footer`
  text-align: center;
  padding: 1rem;
  margin-top: 2rem;
  color: #7f8c8d;
  font-size: 0.9rem;
  border-top: 1px solid #ecf0f1;
  height: 40px;
`;

const BlockInfo = styled.div`
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #7f8c8d;
`;

function App() {
  const [selectedBlockNumber, setSelectedBlockNumber] = useState<string | null>(null);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Checking connection...');
  const [activeView, setActiveView] = useState<ViewType>('graph');
  const [backendStatus, setBackendStatus] = useState<{ connected: boolean; demoMode: boolean; message: string; minBlockNumber?: string }>({
    connected: false,
    demoMode: true,
    message: 'Connecting to backend...'
  });

  useEffect(() => {
    // Check backend status
    const checkStatus = async () => {
      try {
        const response = await api.get('/status');
        setBackendStatus({
          connected: true,
          demoMode: response.data.demo_mode,
          message: response.data.message,
          minBlockNumber: response.data.min_block_number
        });
      } catch (error) {
        setBackendStatus({
          connected: false,
          demoMode: true,
          message: 'Failed to connect to backend'
        });
      }
    };

    checkStatus();
    
    // Poll every 30 seconds to check connection status
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleGraphSelect = (blockNumber: string) => {
    setSelectedBlockNumber(blockNumber);
  };

  const handleBackToRecentGraphs = () => {
    setSelectedBlockNumber(null);
  };

  const handleViewToggle = (view: ViewType) => {
    setActiveView(view);
  };

  const renderViewer = () => {
    if (!selectedBlockNumber) return null;

    if (activeView === 'graph') {
      return <GraphViewer blockNumber={selectedBlockNumber} onBack={handleBackToRecentGraphs} />;
    } else {
      return <GanttViewer blockNumber={selectedBlockNumber} onBack={handleBackToRecentGraphs} />;
    }
  };

  return (
    <>
      <GlobalStyle />
      <AppContainer>
        <Header>
          <Title>Ethereum Transaction Dependency Graphs</Title>
          <Subtitle>Visualize transaction dependencies within Ethereum blocks</Subtitle>
          
          <StatusIndicator isConnected={backendStatus.connected}>
            <StatusDot isConnected={backendStatus.connected} />
            {backendStatus.message}
          </StatusIndicator>
          
          {backendStatus.minBlockNumber && (
            <BlockInfo>
              Available from block #{backendStatus.minBlockNumber}
            </BlockInfo>
          )}
        </Header>
        
        <Main>
          {backendStatus.demoMode && (
            <DemoBanner>
              ⚠️ Running in demo mode with mock data. Set GOOGLE_APPLICATION_CREDENTIALS environment variable for production use.
            </DemoBanner>
          )}
          
          {selectedBlockNumber ? (
            <>
              <ViewToggle activeView={activeView} onViewChange={handleViewToggle} />
              {renderViewer()}
            </>
          ) : (
            <>
              <GraphSearch onSearch={handleGraphSelect} />
              <RecentGraphs onGraphSelect={handleGraphSelect} />
            </>
          )}
        </Main>
        
        <Footer>
          Built with 🖤 by Toni Wahrstätter
        </Footer>
      </AppContainer>
    </>
  );
}

export default App;
