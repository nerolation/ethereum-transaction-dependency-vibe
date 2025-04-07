import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';

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

const DemoTag = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #f39c12;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  z-index: 2;
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

const DemoModeMessage = styled.div`
  text-align: center;
  padding: 1rem;
  margin-top: 1rem;
  color: #f39c12;
  font-size: 1rem;
  background-color: #fff8e1;
  border-radius: 8px;
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

const RecentGraphs: React.FC<RecentGraphsProps> = ({ onGraphSelect }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [graphs, setGraphs] = useState<GraphData[]>([]);
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    const fetchRecentGraphs = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await axios.get('http://localhost:5000/api/recent_graphs');
        setGraphs(response.data);
        
        // Check if any of the graphs are in demo mode
        if (response.data.length > 0 && response.data[0].demo_mode) {
          setIsDemoMode(true);
        }
      } catch (err) {
        setError('Failed to load recent graphs.');
        console.error('Error fetching recent graphs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentGraphs();
  }, []);

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

  if (error) {
    return (
      <Container>
        <SectionTitle>Recent Blocks</SectionTitle>
        <ErrorMessage>{error}</ErrorMessage>
      </Container>
    );
  }

  if (graphs.length === 0) {
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
      
      {isDemoMode && (
        <DemoModeMessage>
          ⚠️ Displaying mock data. Set GOOGLE_APPLICATION_CREDENTIALS to use real data.
        </DemoModeMessage>
      )}
      
      <GraphGrid>
        {graphs.map((graph) => (
          <GraphCard key={graph.block_number} onClick={() => onGraphSelect(graph.block_number)}>
            {graph.demo_mode && <DemoTag>DEMO</DemoTag>}
            <GraphImageContainer>
              <img 
                src={`data:image/png;base64,${graph.image}`} 
                alt={`Transaction Dependency Graph for Block ${graph.block_number}`} 
              />
            </GraphImageContainer>
            <GraphInfo>
              <GraphBlockNumber>Block #{graph.block_number}</GraphBlockNumber>
              <GraphStats>
                <span>Nodes: {graph.node_count}</span>
                <span>Edges: {graph.edge_count}</span>
              </GraphStats>
              <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.85rem' }}>
                <a 
                  href={`https://beaconcha.in/block/${graph.block_number}`} 
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