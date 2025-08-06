import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  Chip,
  LinearProgress,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AutoFixHigh as AIIcon,
  ExpandMore as ExpandMoreIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
  Lightbulb as InsightIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import axios from 'axios';

interface AIInsight {
  type: 'recommendation' | 'alert' | 'optimization' | 'prediction';
  title: string;
  description: string;
  confidence: number;
  impact: string;
  priority: 'high' | 'medium' | 'low';
  actionable: boolean;
}

interface PredictiveAlert {
  type: string;
  message: string;
  priority_score: number;
  action_suggested?: string;
  potential_gain?: number;
  risk_level?: string;
  optimal_timing?: string;
}

interface OptimizationDecision {
  action: string;
  target_id: string;
  confidence: number;
  reasoning: string;
  parameters: any;
  estimated_impact: any;
}

export const AIInsightsDashboard: React.FC = () => {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [alerts, setAlerts] = useState<PredictiveAlert[]>([]);
  const [optimizationResults, setOptimizationResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAIInsights = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch AI insights
      const insightsResponse = await axios.get('/api/v1/analytics/ai-insights');
      
      // Fetch predictive alerts
      const alertsResponse = await axios.get('/api/v1/automation/predictive-alerts', {
        params: { priority_threshold: 60 }
      });

      // Process insights data
      const processedInsights = processInsightsData(insightsResponse.data);
      setInsights(processedInsights);
      setAlerts(alertsResponse.data.alerts || []);

    } catch (err: any) {
      console.error('Error fetching AI insights:', err);
      setError('Failed to fetch AI insights. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const runPortfolioOptimization = async (type: 'aggressive' | 'balanced' | 'conservative' = 'balanced') => {
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/automation/portfolio-optimization', {
        optimization_type: type,
        execute_automatic: false
      });
      
      setOptimizationResults(response.data.results);
    } catch (err: any) {
      console.error('Optimization error:', err);
      setError('Failed to run portfolio optimization.');
    } finally {
      setLoading(false);
    }
  };

  const processInsightsData = (data: any): AIInsight[] => {
    const insights: AIInsight[] = [];

    // Process AI insights
    if (data.ai_insights?.recommendations) {
      data.ai_insights.recommendations.forEach((rec: string, index: number) => {
        insights.push({
          type: 'recommendation',
          title: `Portfolio Recommendation ${index + 1}`,
          description: rec,
          confidence: 75 + Math.random() * 20, // Mock confidence
          impact: 'Medium',
          priority: 'medium',
          actionable: true
        });
      });
    }

    // Process market sentiment
    if (data.market_sentiment) {
      Object.entries(data.market_sentiment).forEach(([team, sentiment]: [string, any]) => {
        insights.push({
          type: 'prediction',
          title: `${team} Market Sentiment`,
          description: `${sentiment.sentiment_label} sentiment with ${sentiment.confidence}% confidence. ${sentiment.reasoning}`,
          confidence: sentiment.confidence || 70,
          impact: sentiment.price_prediction === 'increase' ? 'Positive' : 'Neutral',
          priority: sentiment.confidence > 80 ? 'high' : 'medium',
          actionable: true
        });
      });
    }

    return insights;
  };

  useEffect(() => {
    fetchAIInsights();
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'recommendation': return <InsightIcon />;
      case 'alert': return <WarningIcon />;
      case 'optimization': return <AIIcon />;
      case 'prediction': return <TrendingUpIcon />;
      default: return <InfoIcon />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          AI Insights Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            onClick={() => runPortfolioOptimization('balanced')}
            startIcon={<AIIcon />}
            disabled={loading}
          >
            Run Optimization
          </Button>
          <IconButton onClick={fetchAIInsights} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* AI Insights Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Insights & Recommendations
              </Typography>
              
              {insights.length > 0 ? (
                <Box>
                  {insights.map((insight, index) => (
                    <Accordion key={index}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                          {getTypeIcon(insight.type)}
                          <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                            {insight.title}
                          </Typography>
                          <Chip 
                            label={insight.priority.toUpperCase()} 
                            size="small" 
                            color={getPriorityColor(insight.priority) as any}
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" paragraph>
                          {insight.description}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                          <Typography variant="caption" color="text.secondary">
                            Confidence: {insight.confidence.toFixed(0)}%
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Impact: {insight.impact}
                          </Typography>
                          {insight.actionable && (
                            <Chip label="Actionable" size="small" color="success" />
                          )}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              ) : (
                <Typography color="text.secondary">
                  No insights available. Click refresh to generate new insights.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Predictive Alerts Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Predictive Alerts
              </Typography>
              
              {alerts.length > 0 ? (
                <List dense>
                  {alerts.map((alert, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemIcon>
                          {alert.type === 'price_opportunity' ? (
                            <TrendingUpIcon color="success" />
                          ) : alert.type === 'market_risk' ? (
                            <WarningIcon color="warning" />
                          ) : (
                            <InfoIcon color="info" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={alert.message}
                          secondary={
                            <Box sx={{ mt: 1 }}>
                              <Chip 
                                label={`Priority: ${alert.priority_score}`} 
                                size="small" 
                                variant="outlined"
                              />
                              {alert.potential_gain && (
                                <Chip 
                                  label={`+$${alert.potential_gain}`} 
                                  size="small" 
                                  color="success"
                                  sx={{ ml: 1 }}
                                />
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < alerts.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No active alerts. The AI is monitoring your portfolio for opportunities.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Optimization Results Section */}
        {optimizationResults && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Portfolio Optimization Results
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom>
                          Portfolio Health
                        </Typography>
                        <Typography variant="h4">
                          {optimizationResults.portfolio_health?.health_score?.toFixed(0) || 'N/A'}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom>
                          Optimization Decisions
                        </Typography>
                        <Typography variant="h4">
                          {optimizationResults.optimization_decisions?.length || 0}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom>
                          Projected Revenue Impact
                        </Typography>
                        <Typography variant="h4" color="success.main">
                          ${optimizationResults.projected_impact?.projected_revenue_impact?.toFixed(2) || '0.00'}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom>
                          Average Confidence
                        </Typography>
                        <Typography variant="h4">
                          {optimizationResults.projected_impact?.average_confidence?.toFixed(0) || 0}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
                
                {optimizationResults.optimization_decisions?.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Recommended Actions
                    </Typography>
                    {optimizationResults.optimization_decisions.map((decision: OptimizationDecision, index: number) => (
                      <Alert 
                        key={index} 
                        severity="info" 
                        sx={{ mb: 1 }}
                        action={
                          <Button size="small" color="inherit">
                            Apply
                          </Button>
                        }
                      >
                        <strong>{decision.action}:</strong> {decision.reasoning} 
                        <em> (Confidence: {decision.confidence}%)</em>
                      </Alert>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default AIInsightsDashboard;