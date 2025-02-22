import React, { useEffect, useState, useCallback } from 'react';
import {
    Grid,
    Paper,
    Typography,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Switch,
    FormControlLabel,
    CircularProgress,
} from '@mui/material';
import {
    Edit as EditIcon,
    Delete as DeleteIcon,
    Add as AddIcon,
} from '@mui/icons-material';
import { getTemplates, createTemplate, updateTemplate, deleteTemplate } from '../../services/api';
import { MessageTemplate } from '../../types/api';

const Templates = () => {
    const [templates, setTemplates] = useState<MessageTemplate[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [editingTemplate, setEditingTemplate] = useState<MessageTemplate | null>(null);
    const [formData, setFormData] = useState({
        trigger_text: '',
        response_text: '',
        is_active: true,
    });

    const fetchTemplates = useCallback(async () => {
        try {
            const response = await getTemplates();
            setTemplates(response.data.data);
        } catch (err) {
            setError('Şablonlar yüklenirken bir hata oluştu.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTemplates();
    }, [fetchTemplates]);

    const handleOpenDialog = (template?: MessageTemplate) => {
        if (template) {
            setEditingTemplate(template);
            setFormData({
                trigger_text: template.trigger_text,
                response_text: template.response_text,
                is_active: template.is_active,
            });
        } else {
            setEditingTemplate(null);
            setFormData({
                trigger_text: '',
                response_text: '',
                is_active: true,
            });
        }
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setEditingTemplate(null);
    };

    const handleSubmit = async () => {
        try {
            if (editingTemplate) {
                await updateTemplate(editingTemplate.id, formData);
            } else {
                await createTemplate(formData);
            }
            handleCloseDialog();
            fetchTemplates();
        } catch (err) {
            console.error('Şablon kaydedilirken hata oluştu:', err);
            setError('Şablon kaydedilirken bir hata oluştu.');
        }
    };

    const handleDelete = async (id: number) => {
        if (window.confirm('Bu şablonu silmek istediğinizden emin misiniz?')) {
            try {
                await deleteTemplate(id);
                fetchTemplates();
            } catch (err) {
                console.error('Şablon silinirken hata oluştu:', err);
                setError('Şablon silinirken bir hata oluştu.');
            }
        }
    };

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
            <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h4">Mesaj Şablonları</Typography>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDialog()}
                >
                    Yeni Şablon
                </Button>
            </Grid>

            <Grid item xs={12}>
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Tetikleyici Mesaj</TableCell>
                                <TableCell>Yanıt Mesajı</TableCell>
                                <TableCell>Durum</TableCell>
                                <TableCell>İşlemler</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {templates.map((template) => (
                                <TableRow key={template.id}>
                                    <TableCell>{template.trigger_text}</TableCell>
                                    <TableCell>{template.response_text}</TableCell>
                                    <TableCell>{template.is_active ? 'Aktif' : 'Pasif'}</TableCell>
                                    <TableCell>
                                        <IconButton onClick={() => handleOpenDialog(template)} color="primary">
                                            <EditIcon />
                                        </IconButton>
                                        <IconButton onClick={() => handleDelete(template.id)} color="error">
                                            <DeleteIcon />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Grid>

            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {editingTemplate ? 'Şablon Düzenle' : 'Yeni Şablon'}
                </DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Tetikleyici Mesaj"
                        type="text"
                        fullWidth
                        value={formData.trigger_text}
                        onChange={(e) => setFormData({ ...formData, trigger_text: e.target.value })}
                    />
                    <TextField
                        margin="dense"
                        label="Yanıt Mesajı"
                        type="text"
                        fullWidth
                        multiline
                        rows={4}
                        value={formData.response_text}
                        onChange={(e) => setFormData({ ...formData, response_text: e.target.value })}
                    />
                    <FormControlLabel
                        control={
                            <Switch
                                checked={formData.is_active}
                                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                color="primary"
                            />
                        }
                        label="Aktif"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>İptal</Button>
                    <Button onClick={handleSubmit} color="primary">
                        Kaydet
                    </Button>
                </DialogActions>
            </Dialog>
        </Grid>
    );
};

export default Templates; 