import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { fetchWithCache } from '../api';
import { graphImageCache } from './GraphViewer';

const Container = styled.div`
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  text-align: center;
`;

const GraphGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
`;

const GraphCard = styled.div`
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  position: relative;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
`;

const GraphImageContainer = styled.div`
  width: 100%;
  height: 220px;
  overflow: hidden;
  position: relative;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const LoadingSpinner = styled.div`
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const GraphInfo = styled.div`
  padding: 1.5rem;
`;

const GraphBlockNumber = styled.h3`
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  text-align: center;
`;

const GraphStats = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #7f8c8d;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
  font-size: 1.2rem;
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 3rem;
  color: #e74c3c;
  font-size: 1.2rem;
`;

interface RecentGraphsProps {
  onGraphSelect: (blockNumber: string) => void;
}

interface GraphData {
  block_number: string;
  image: string; // base64 encoded image
  node_count: number;
  edge_count: number;
  demo_mode: boolean;
}

interface GraphCardState {
  loading: boolean;
  imageLoaded: boolean;
  data: GraphData | null;
}

const RecentGraphs: React.FC<RecentGraphsProps> = ({ onGraphSelect }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [blockNumbers, setBlockNumbers] = useState<string[]>([]);
  const [graphCards, setGraphCards] = useState<{[key: string]: GraphCardState}>({});

  // First, fetch just the list of recent blocks
  useEffect(() => {
    const fetchRecentBlocks = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Get recent graphs data with caching
        const data = await fetchWithCache('/recent_graphs');
        
        // Extract block numbers and set up initial card states
        const blocks = data.map((graph: GraphData) => graph.block_number);
        setBlockNumbers(blocks);
        
        // Initialize graph cards state
        const initialGraphCards: {[key: string]: GraphCardState} = {};
        data.forEach((graph: GraphData) => {
          // Pre-load images into browser cache when data is available
          if (graph.image) {
            graphImageCache.set(graph.block_number, graph.image);
            
            // Create an image object to trigger browser caching
            const img = new Image();
            img.src = `data:image/png;base64,${graph.image}`;
            
            // When image loads, mark it as loaded in our state
            img.onload = () => {
              setGraphCards(prev => ({
                ...prev,
                [graph.block_number]: { 
                  ...prev[graph.block_number], 
                  imageLoaded: true 
                }
              }));
            };
          }
          
          initialGraphCards[graph.block_number] = {
            loading: false,
            imageLoaded: false,
            data: graph
          };
        });
        
        setGraphCards(initialGraphCards);
        setLoading(false);
      } catch (err) {
        setError('Failed to load recent graphs.');
        console.error('Error fetching recent graphs:', err);
        setLoading(false);
      }
    };

    fetchRecentBlocks();
  }, []);

  const handleImageLoad = (blockNumber: string) => {
    setGraphCards(prev => ({
      ...prev,
      [blockNumber]: { ...prev[blockNumber], imageLoaded: true }
    }));
  };

  // Loading state
  if (loading) {
    return (
      <Container>
        <SectionTitle>Recent Blocks</SectionTitle>
        <LoadingMessage>
          <LoadingSpinner />
          <div>Loading recent graphs...</div>
        </LoadingMessage>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container>
        <SectionTitle>Recent Blocks</SectionTitle>
        <ErrorMessage>{error}</ErrorMessage>
      </Container>
    );
  }

  // No data state
  if (blockNumbers.length === 0) {
    return (
      <Container>
        <SectionTitle>Recent Blocks</SectionTitle>
        <ErrorMessage>No recent graphs available.</ErrorMessage>
      </Container>
    );
  }

  return (
    <Container>
      <SectionTitle>Recent Blocks</SectionTitle>
      
      <GraphGrid>
        {blockNumbers.map((blockNumber) => (
          <GraphCard key={blockNumber} onClick={() => onGraphSelect(blockNumber)}>
            <GraphImageContainer>
              {graphCards[blockNumber]?.loading && (
                <LoadingSpinner />
              )}
              
              {graphCards[blockNumber]?.data && (
                <>
                  {!graphCards[blockNumber].imageLoaded && <LoadingSpinner />}
                  <img 
                    src={`data:image/png;base64,${graphCards[blockNumber].data?.image}`} 
                    alt={`Transaction Dependency Graph for Block ${blockNumber}`}
                    style={{ display: graphCards[blockNumber].imageLoaded ? 'block' : 'none' }}
                    onLoad={() => handleImageLoad(blockNumber)}
                    loading="lazy"
                  />
                </>
              )}
              
              {!graphCards[blockNumber]?.loading && !graphCards[blockNumber]?.data && (
                <div>Failed to load</div>
              )}
            </GraphImageContainer>
            
            <GraphInfo>
              <GraphBlockNumber>Block #{blockNumber}</GraphBlockNumber>
              <GraphStats>
                <span>Nodes: {graphCards[blockNumber]?.data?.node_count || '...'}</span>
                <span>Edges: {graphCards[blockNumber]?.data?.edge_count || '...'}</span>
              </GraphStats>
              <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.85rem' }}>
                <a 
                  href={`https://beaconcha.in/block/${blockNumber}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ color: '#3498db', textDecoration: 'none' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  View on beaconcha.in
                </a>
              </div>
            </GraphInfo>
          </GraphCard>
        ))}
      </GraphGrid>
    </Container>
  );
};

export default RecentGraphs; 