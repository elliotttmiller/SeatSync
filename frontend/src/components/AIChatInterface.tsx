import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
  IconButton,
  Avatar,
  CircularProgress
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
  AutoFixHigh as MagicIcon
} from '@mui/icons-material';
import axios from 'axios';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface ChatSuggestion {
  text: string;
  category: 'pricing' | 'portfolio' | 'market' | 'general';
}

export const AIChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m SeatSync AI, your intelligent ticket portfolio assistant. I can help you with pricing strategies, market analysis, portfolio optimization, and more. What would you like to know?',
      timestamp: new Date().toISOString()
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([
    'Analyze my current portfolio',
    'Get price predictions for my tickets',
    'Show me market opportunities',
    'Help me optimize my pricing strategy'
  ]);

  const sendMessage = async () => {
    if (!currentMessage.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/v1/chat', {
        message: currentMessage,
        conversation_history: messages.slice(-5), // Last 5 messages for context
        user_context: {
          conversation_id: 'main',
          user_id: 'demo_user'
        },
        portfolio_context: true
      });

      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Update suggestions if provided
      if (response.data.suggestions) {
        setSuggestions(response.data.suggestions);
      }

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'I apologize, but I\'m experiencing technical difficulties. Please try again later.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setCurrentMessage(suggestion);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <Card sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <AIIcon />
          </Avatar>
          <Box>
            <Typography variant="h6">SeatSync AI Assistant</Typography>
            <Typography variant="caption" color="text.secondary">
              Intelligent ticket portfolio management
            </Typography>
          </Box>
        </Box>
      </CardContent>

      <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
        <List sx={{ py: 0 }}>
          {messages.map((message, index) => (
            <ListItem key={index} sx={{ px: 1, alignItems: 'flex-start' }}>
              <Avatar 
                sx={{ 
                  mr: 1, 
                  mt: 0.5, 
                  width: 32, 
                  height: 32,
                  bgcolor: message.role === 'user' ? 'grey.500' : 'primary.main'
                }}
              >
                {message.role === 'user' ? <PersonIcon /> : <AIIcon />}
              </Avatar>
              <Paper 
                elevation={1}
                sx={{ 
                  p: 2, 
                  maxWidth: '80%',
                  bgcolor: message.role === 'user' ? 'grey.100' : 'primary.50',
                  borderRadius: 2
                }}
              >
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
                {message.timestamp && (
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </Typography>
                )}
              </Paper>
            </ListItem>
          ))}
          {isLoading && (
            <ListItem sx={{ px: 1, justifyContent: 'center' }}>
              <CircularProgress size={24} />
            </ListItem>
          )}
        </List>
      </Box>

      {suggestions.length > 0 && (
        <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
            Quick suggestions:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {suggestions.map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                size="small"
                onClick={() => handleSuggestionClick(suggestion)}
                clickable
                variant="outlined"
                icon={<MagicIcon />}
              />
            ))}
          </Box>
        </Box>
      )}

      <Divider />

      <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          placeholder="Ask me about your ticket portfolio..."
          value={currentMessage}
          onChange={(e) => setCurrentMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          variant="outlined"
          size="small"
        />
        <Button
          variant="contained"
          onClick={sendMessage}
          disabled={!currentMessage.trim() || isLoading}
          sx={{ minWidth: 48 }}
        >
          <SendIcon />
        </Button>
      </Box>
    </Card>
  );
};

export default AIChatInterface;