import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import GraphViewer from './components/GraphViewer';
import GanttViewer from './components/GanttViewer';
import GraphSearch from './components/GraphSearch';
import RecentGraphs from './components/RecentGraphs';
import ViewToggle, { ViewType } from './components/ViewToggle';
import { GlobalStyle } from './styles/GlobalStyle';
import { getMinBlockNumber } from './api';

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

const GithubLink = styled.a`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  color: #3498db;
  text-decoration: none;
  transition: color 0.2s;
  
  &:hover {
    color: #2980b9;
    text-decoration: underline;
  }
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
  const [activeView, setActiveView] = useState<ViewType>('graph');
  const [backendStatus, setBackendStatus] = useState<{ connected: boolean; minBlockNumber?: string }>({
    connected: false
  });

  useEffect(() => {
    // Check backend status by loading minimum block number
    const checkStatus = async () => {
      try {
        const minBlockNumber = await getMinBlockNumber();
        setBackendStatus({
          connected: true,
          minBlockNumber
        });
      } catch (error) {
        console.error('Error checking status:', error);
        setBackendStatus({
          connected: false
        });
      }
    };

    checkStatus();
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
          
          <GithubLink href="https://github.com/nerolation/dependency.pics" target="_blank" rel="noopener noreferrer">
            <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
              <path fillRule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            GitHub Repository
          </GithubLink>
          
          {backendStatus.minBlockNumber && (
            <BlockInfo>
              Available from block #{backendStatus.minBlockNumber}
            </BlockInfo>
          )}
        </Header>
        
        <Main>
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
