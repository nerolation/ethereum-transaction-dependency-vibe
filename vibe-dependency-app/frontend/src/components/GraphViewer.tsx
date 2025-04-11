import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import api, { fetchWithCache } from '../api';

const GraphContainer = styled.div`
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
`;

const GraphHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;

const GraphTitle = styled.h2`
  font-size: 1.5rem;
  color: #2c3e50;
`;

const BackButton = styled.button`
  display: flex;
  align-items: center;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #2980b9;
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.5);
  }
`;

const GraphStats = styled.div`
  display: flex;
  gap: 1.5rem;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  font-size: 0.95rem;
`;

const StatLabel = styled.span`
  color: #7f8c8d;
  margin-right: 0.5rem;
`;

const StatValue = styled.span`
  font-weight: 600;
  color: #2c3e50;
`;

const GraphImage = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 100%;
  overflow: hidden;
  
  img {
    max-width: 100%;
    max-height: 600px;
    object-fit: contain;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
`;

const LoadingSpinner = styled.div`
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #7f8c8d;
  font-size: 1.2rem;
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 3rem;
  color: #e74c3c;
  font-size: 1.2rem;
`;

const DemoModeTag = styled.div`
  display: inline-block;
  background-color: #f39c12;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-left: 1rem;
`;

// Add a new styled component for the image placeholder
const ImagePlaceholder = styled.div`
  width: 100%;
  height: 450px;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
`;

// Client-side cache for graph images
export const graphImageCache = new Map<string, string>();

interface GraphViewerProps {
  blockNumber: string;
  onBack?: () => void;
}

interface GraphData {
  block_number: string;
  image: string; // base64 encoded image
  node_count: number;
  edge_count: number;
  demo_mode: boolean;
}

const GraphViewer: React.FC<GraphViewerProps> = ({ blockNumber, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [imageLoaded, setImageLoaded] = useState(false);

  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      setError(null);
      setImageLoaded(false);
      
      try {
        // Use the fetchWithCache helper to get data with caching
        const data = await fetchWithCache(`/graph/${blockNumber}`);
        setGraphData(data);
        
        // Cache the image data for reuse
        if (data.image) {
          graphImageCache.set(blockNumber, data.image);
        }
      } catch (err) {
        setError('Failed to load graph. The block number may not exist or there was a server error.');
        console.error('Error fetching graph:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [blockNumber]);

  if (loading) {
    return (
      <GraphContainer>
        <LoadingContainer>
          <LoadingSpinner />
          <LoadingMessage>Loading graph for block {blockNumber}...</LoadingMessage>
        </LoadingContainer>
      </GraphContainer>
    );
  }

  if (error) {
    return (
      <GraphContainer>
        <ErrorMessage>{error}</ErrorMessage>
      </GraphContainer>
    );
  }

  if (!graphData) {
    return (
      <GraphContainer>
        <ErrorMessage>No graph data available.</ErrorMessage>
      </GraphContainer>
    );
  }

  return (
    <GraphContainer>
      <GraphHeader>
        <GraphTitle>
          Block #{graphData.block_number}
        </GraphTitle>
        <BackButton onClick={onBack}>
          ← Back to Recent Blocks
        </BackButton>
      </GraphHeader>
      
      <GraphStats>
        <StatItem>
          <StatLabel>Nodes:</StatLabel>
          <StatValue>{graphData.node_count}</StatValue>
        </StatItem>
        <StatItem>
          <StatLabel>Edges:</StatLabel>
          <StatValue>{graphData.edge_count}</StatValue>
        </StatItem>
        <StatItem>
          <StatLabel>View on:</StatLabel>
          <StatValue>
            <a 
              href={`https://beaconcha.in/block/${graphData.block_number}`} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#3498db', textDecoration: 'none' }}
            >
              beaconcha.in
            </a>
          </StatValue>
        </StatItem>
      </GraphStats>
      
      <GraphImage>
        {!imageLoaded && (
          <ImagePlaceholder>
            <LoadingSpinner />
          </ImagePlaceholder>
        )}
        <img 
          src={`data:image/png;base64,${graphData.image}`}
          alt={`Transaction Dependency Graph for Block ${graphData.block_number}`}
          style={{ display: imageLoaded ? 'block' : 'none' }}
          onLoad={() => setImageLoaded(true)}
        />
      </GraphImage>
    </GraphContainer>
  );
};

export default GraphViewer; 