import React, { useEffect, useState, useCallback } from 'react';
import {
    Grid,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    TextField,
    CircularProgress,
    Box,
} from '@mui/material';
import { getMessageLogs } from '../../services/api';
import { MessageLog } from '../../types/api';

const History = () => {
    const [messages, setMessages] = useState<MessageLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchMessages = useCallback(async () => {
        try {
            const response = await getMessageLogs(page + 1, rowsPerPage);
            setMessages(response.data.data);
        } catch (err) {
            setError('Mesaj geçmişi yüklenirken bir hata oluştu.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [page, rowsPerPage]);

    useEffect(() => {
        fetchMessages();
    }, [fetchMessages]);

    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const filteredMessages = messages.filter(message =>
        message.incoming_message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        message.response_message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        message.user_id.includes(searchTerm)
    );

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
                    Mesaj Geçmişi
                </Typography>
            </Grid>

            <Grid item xs={12}>
                <Box sx={{ mb: 2 }}>
                    <TextField
                        fullWidth
                        label="Ara"
                        variant="outlined"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Mesaj içeriği veya kullanıcı ID'si ile arayın..."
                    />
                </Box>
            </Grid>

            <Grid item xs={12}>
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Kullanıcı ID</TableCell>
                                <TableCell>Gelen Mesaj</TableCell>
                                <TableCell>Yanıt</TableCell>
                                <TableCell>Tarih</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {filteredMessages.map((message) => (
                                <TableRow key={message.id}>
                                    <TableCell>{message.user_id}</TableCell>
                                    <TableCell>{message.incoming_message}</TableCell>
                                    <TableCell>{message.response_message}</TableCell>
                                    <TableCell>
                                        {new Date(message.created_at).toLocaleString()}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
                <TablePagination
                    component="div"
                    count={-1}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                    rowsPerPageOptions={[5, 10, 25, 50]}
                    labelRowsPerPage="Sayfa başına satır:"
                    labelDisplayedRows={({ from, to }) => `${from}-${to} arası gösteriliyor`}
                />
            </Grid>
        </Grid>
    );
};

export default History; 