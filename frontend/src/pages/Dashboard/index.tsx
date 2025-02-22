import React, { useEffect, useState } from 'react';
import {
    Grid,
    Paper,
    Typography,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemText,
    CircularProgress,
} from '@mui/material';
import { getDashboardStats } from '../../services/api';
import { DashboardStats } from '../../types/api';

const Dashboard = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await getDashboardStats();
                setStats(response.data.data);
            } catch (err) {
                setError('İstatistikler yüklenirken bir hata oluştu.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return (
            <Grid container justifyContent="center" alignItems="center" style={{ minHeight: '400px' }}>
                <CircularProgress />
            </Grid>
        );
    }

    if (error) {
        return (
            <Typography color="error" align="center">
                {error}
            </Typography>
        );
    }

    return (
        <Grid container spacing={3}>
            <Grid item xs={12}>
                <Typography variant="h4" gutterBottom>
                    Dashboard
                </Typography>
            </Grid>

            {/* İstatistik Kartları */}
            <Grid item xs={12} md={4}>
                <Card>
                    <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                            Toplam Mesaj
                        </Typography>
                        <Typography variant="h3">
                            {stats?.total_messages || 0}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} md={4}>
                <Card>
                    <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                            Aktif Şablonlar
                        </Typography>
                        <Typography variant="h3">
                            {stats?.active_templates || 0}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            <Grid item xs={12} md={4}>
                <Card>
                    <CardContent>
                        <Typography color="textSecondary" gutterBottom>
                            Yanıt Oranı
                        </Typography>
                        <Typography variant="h3">
                            {`%${stats?.response_rate.toFixed(1) || 0}`}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>

            {/* Son Mesajlar */}
            <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                        Son Mesajlar
                    </Typography>
                    <List>
                        {stats?.recent_messages.map((message) => (
                            <ListItem key={message.id} divider>
                                <ListItemText
                                    primary={message.incoming_message}
                                    secondary={
                                        <>
                                            <Typography component="span" variant="body2" color="textPrimary">
                                                Yanıt: {message.response_message}
                                            </Typography>
                                            <br />
                                            <Typography component="span" variant="body2" color="textSecondary">
                                                {new Date(message.created_at).toLocaleString()}
                                            </Typography>
                                        </>
                                    }
                                />
                            </ListItem>
                        ))}
                    </List>
                </Paper>
            </Grid>
        </Grid>
    );
};

export default Dashboard; 