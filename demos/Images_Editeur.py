#!/usr/bin/env python3
"""
Exemple 06: Éditeur d'images avec filtres et transformations
Fonctionnalités: Édition d'images, filtres, rotations, redimensionnement, histogramme
"""

import PySimpleGUI4 as sg
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
import io
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sg.theme('DarkTeal12')

class ImageEditor:
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.image_history = []
        self.history_index = -1
        self.current_file = None
        
    def load_image(self, filename):
        """Charge une image"""
        try:
            image = Image.open(filename)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            self.original_image = image.copy()
            self.current_image = image.copy()
            self.current_file = filename
            
            # Initialiser l'historique
            self.image_history = [image.copy()]
            self.history_index = 0
            
            return True
        except Exception as e:
            sg.popup_error(f'Erreur lors du chargement: {str(e)}')
            return False
    
    def save_to_history(self):
        """Sauvegarde l'état actuel dans l'historique"""
        if self.current_image:
            # Supprimer l'historique après l'index actuel
            self.image_history = self.image_history[:self.history_index + 1]
            # Ajouter la nouvelle image
            self.image_history.append(self.current_image.copy())
            self.history_index += 1
            
            # Limiter l'historique à 20 états
            if len(self.image_history) > 20:
                self.image_history.pop(0)
                self.history_index -= 1
    
    def undo(self):
        """Annuler la dernière action"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.image_history[self.history_index].copy()
            return True
        return False
    
    def redo(self):
        """Refaire l'action suivante"""
        if self.history_index < len(self.image_history) - 1:
            self.history_index += 1
            self.current_image = self.image_history[self.history_index].copy()
            return True
        return False
    
    def image_to_bytes(self, image, max_size=(800, 600)):
        """Convertit une image PIL en bytes pour PySimpleGUI"""
        if image:
            # Redimensionner pour l'affichage si nécessaire
            display_image = image.copy()
            display_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            bio = io.BytesIO()
            display_image.save(bio, format='PNG')
            bio.seek(0)
            return bio.getvalue()
        return None
    
    def apply_filter(self, filter_type):
        """Applique un filtre à l'image"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        
        if filter_type == 'blur':
            self.current_image = self.current_image.filter(ImageFilter.BLUR)
        elif filter_type == 'sharpen':
            self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
        elif filter_type == 'edge':
            self.current_image = self.current_image.filter(ImageFilter.FIND_EDGES)
        elif filter_type == 'emboss':
            self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
        elif filter_type == 'smooth':
            self.current_image = self.current_image.filter(ImageFilter.SMOOTH)
        elif filter_type == 'detail':
            self.current_image = self.current_image.filter(ImageFilter.DETAIL)
        elif filter_type == 'contour':
            self.current_image = self.current_image.filter(ImageFilter.CONTOUR)
        
        return True
    
    def adjust_brightness(self, factor):
        """Ajuste la luminosité (factor: 0.0 = noir, 1.0 = original, 2.0 = double)"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        enhancer = ImageEnhance.Brightness(self.current_image)
        self.current_image = enhancer.enhance(factor)
        return True
    
    def adjust_contrast(self, factor):
        """Ajuste le contraste"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        enhancer = ImageEnhance.Contrast(self.current_image)
        self.current_image = enhancer.enhance(factor)
        return True
    
    def adjust_color(self, factor):
        """Ajuste la saturation des couleurs"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        enhancer = ImageEnhance.Color(self.current_image)
        self.current_image = enhancer.enhance(factor)
        return True
    
    def rotate_image(self, angle):
        """Fait tourner l'image"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        self.current_image = self.current_image.rotate(angle, expand=True)
        return True
    
    def flip_image(self, direction):
        """Retourne l'image (horizontal ou vertical)"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        if direction == 'horizontal':
            self.current_image = ImageOps.mirror(self.current_image)
        elif direction == 'vertical':
            self.current_image = ImageOps.flip(self.current_image)
        return True
    
    def resize_image(self, width, height, maintain_aspect=True):
        """Redimensionne l'image"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        
        if maintain_aspect:
            self.current_image.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            self.current_image = self.current_image.resize((width, height), Image.Resampling.LANCZOS)
        
        return True
    
    def crop_image(self, left, top, right, bottom):
        """Recadre l'image"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        self.current_image = self.current_image.crop((left, top, right, bottom))
        return True
    
    def convert_to_grayscale(self):
        """Convertit en niveaux de gris"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        grayscale = ImageOps.grayscale(self.current_image)
        self.current_image = grayscale.convert('RGB')
        return True
    
    def add_text(self, text, x, y, font_size=24, color=(255, 255, 255)):
        """Ajoute du texte à l'image"""
        if not self.current_image:
            return False
        
        self.save_to_history()
        draw = ImageDraw.Draw(self.current_image)
        
        try:
            # Essayer d'utiliser une police système
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Utiliser la police par défaut
            font = ImageFont.load_default()
        
        draw.text((x, y), text, fill=color, font=font)
        return True
    
    def get_histogram_data(self):
        """Génère les données d'histogramme de l'image"""
        if not self.current_image:
            return None
        
        # Convertir en numpy array
        img_array = np.array(self.current_image)
        
        # Calculer les histogrammes pour chaque canal
        hist_r = np.histogram(img_array[:,:,0], bins=256, range=(0, 255))[0]
        hist_g = np.histogram(img_array[:,:,1], bins=256, range=(0, 255))[0]
        hist_b = np.histogram(img_array[:,:,2], bins=256, range=(0, 255))[0]
        
        return hist_r, hist_g, hist_b
    
    def create_histogram_plot(self):
        """Crée un graphique d'histogramme"""
        hist_data = self.get_histogram_data()
        if not hist_data:
            return None
        
        hist_r, hist_g, hist_b = hist_data
        
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#3b3b3b')
        
        x = np.arange(256)
        ax.plot(x, hist_r, color='red', alpha=0.7, label='Rouge')
        ax.plot(x, hist_g, color='green', alpha=0.7, label='Vert')
        ax.plot(x, hist_b, color='blue', alpha=0.7, label='Bleu')
        
        ax.set_title('Histogramme des Couleurs', color='white')
        ax.set_xlabel('Valeur de Pixel', color='white')
        ax.set_ylabel('Fréquence', color='white')
        ax.tick_params(colors='white')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Conversion en bytes
        bio = io.BytesIO()
        fig.savefig(bio, format='PNG', facecolor='#2b2b2b', bbox_inches='tight')
        bio.seek(0)
        
        plt.close(fig)
        return bio.getvalue()
    
    def create_layout(self):
        # Menu principal
        menu_def = [
            ['Fichier', ['Ouvrir::CTRL+O', 'Sauvegarder::CTRL+S', 'Sauvegarder sous::CTRL+SHIFT+S', '---', 'Quitter::CTRL+Q']],
            ['Édition', ['Annuler::CTRL+Z', 'Refaire::CTRL+Y', '---', 'Réinitialiser']],
            ['Image', ['Informations', 'Histogramme']],
            ['Aide', ['À propos']]
        ]
        
        # Barre d'outils
        toolbar = [
            sg.Button('📁', key='OPEN', tooltip='Ouvrir', size=(3, 1)),
            sg.Button('💾', key='SAVE', tooltip='Sauvegarder', size=(3, 1)),
            sg.VSeparator(),
            sg.Button('↶', key='UNDO', tooltip='Annuler', size=(3, 1)),
            sg.Button('↷', key='REDO', tooltip='Refaire', size=(3, 1)),
            sg.VSeparator(),
            sg.Button('🔄', key='ROTATE_LEFT', tooltip='Rotation -90°', size=(3, 1)),
            sg.Button('🔃', key='ROTATE_RIGHT', tooltip='Rotation +90°', size=(3, 1)),
            sg.Button('↔️', key='FLIP_H', tooltip='Miroir horizontal', size=(3, 1)),
            sg.Button('↕️', key='FLIP_V', tooltip='Miroir vertical', size=(3, 1)),
        ]
        
        # Panneau des filtres
        filters_panel = [
            [sg.Text('🎨 Filtres', font=('Arial', 12, 'bold'))],
            [sg.Button('Flou', key='FILTER_BLUR', size=(12, 1))],
            [sg.Button('Netteté', key='FILTER_SHARPEN', size=(12, 1))],
            [sg.Button('Contours', key='FILTER_EDGE', size=(12, 1))],
            [sg.Button('Relief', key='FILTER_EMBOSS', size=(12, 1))],
            [sg.Button('Lissage', key='FILTER_SMOOTH', size=(12, 1))],
            [sg.Button('Détail', key='FILTER_DETAIL', size=(12, 1))],
            [sg.Button('N&B', key='GRAYSCALE', size=(12, 1))],
            [sg.HSeparator()],
            [sg.Text('⚖️ Ajustements')],
            [sg.Text('Luminosité:')],
            [sg.Slider(range=(0.1, 3.0), default_value=1.0, resolution=0.1, 
                      orientation='h', key='BRIGHTNESS', size=(15, 15), enable_events=True)],
            [sg.Text('Contraste:')],
            [sg.Slider(range=(0.1, 3.0), default_value=1.0, resolution=0.1,
                      orientation='h', key='CONTRAST', size=(15, 15), enable_events=True)],
            [sg.Text('Saturation:')],
            [sg.Slider(range=(0.0, 3.0), default_value=1.0, resolution=0.1,
                      orientation='h', key='COLOR', size=(15, 15), enable_events=True)]
        ]
        
        # Panneau de transformation
        transform_panel = [
            [sg.Text('🔧 Transformations', font=('Arial', 12, 'bold'))],
            [sg.Text('Rotation:')],
            [sg.Input('0', key='ROTATION_ANGLE', size=(8, 1)), sg.Text('°'),
             sg.Button('Appliquer', key='APPLY_ROTATION')],
            [sg.HSeparator()],
            [sg.Text('Redimensionnement:')],
            [sg.Text('Largeur:'), sg.Input('', key='RESIZE_WIDTH', size=(8, 1))],
            [sg.Text('Hauteur:'), sg.Input('', key='RESIZE_HEIGHT', size=(8, 1))],
            [sg.Checkbox('Maintenir proportions', key='MAINTAIN_ASPECT', default=True)],
            [sg.Button('Redimensionner', key='APPLY_RESIZE')],
            [sg.HSeparator()],
            [sg.Text('Recadrage:')],
            [sg.Text('Gauche:'), sg.Input('0', key='CROP_LEFT', size=(6, 1)),
             sg.Text('Haut:'), sg.Input('0', key='CROP_TOP', size=(6, 1))],
            [sg.Text('Droite:'), sg.Input('100', key='CROP_RIGHT', size=(6, 1)),
             sg.Text('Bas:'), sg.Input('100', key='CROP_BOTTOM', size=(6, 1))],
            [sg.Button('Recadrer', key='APPLY_CROP')]
        ]
        
        # Panneau de texte
        text_panel = [
            [sg.Text('📝 Ajouter Texte', font=('Arial', 12, 'bold'))],
            [sg.Text('Texte:')],
            [sg.Input('', key='TEXT_CONTENT', size=(20, 1))],
            [sg.Text('Position X:'), sg.Input('10', key='TEXT_X', size=(8, 1))],
            [sg.Text('Position Y:'), sg.Input('10', key='TEXT_Y', size=(8, 1))],
            [sg.Text('Taille:'), sg.Input('24', key='TEXT_SIZE', size=(8, 1))],
            [sg.Text('Couleur:'), sg.Combo(['Blanc', 'Noir', 'Rouge', 'Vert', 'Bleu'], 
                                         default_value='Blanc', key='TEXT_COLOR')],
            [sg.Button('Ajouter Texte', key='ADD_TEXT')]
        ]
        
        # Zone d'affichage de l'image
        image_display = [
            [sg.Image(key='IMAGE_DISPLAY', size=(800, 600))]
        ]
        
        # Informations sur l'image
        info_panel = [
            [sg.Text('📊 Informations', font=('Arial', 12, 'bold'))],
            [sg.Text('Fichier:'), sg.Text('Aucun', key='FILE_INFO')],
            [sg.Text('Dimensions:'), sg.Text('0 x 0', key='SIZE_INFO')],
            [sg.Text('Mode:'), sg.Text('', key='MODE_INFO')],
            [sg.Text('Taille:'), sg.Text('0 KB', key='FILE_SIZE')],
            [sg.HSeparator()],
            [sg.Text('📈 Histogramme')],
            [sg.Image(key='HISTOGRAM', size=(300, 200))],
            [sg.Button('Actualiser Histogramme', key='UPDATE_HISTOGRAM')]
        ]
        
        # Layout principal avec onglets pour les outils
        tools_tabs = [
            [sg.TabGroup([
                [sg.Tab('Filtres', filters_panel)],
                [sg.Tab('Transform', transform_panel)],
                [sg.Tab('Texte', text_panel)],
                [sg.Tab('Info', info_panel)]
            ])]
        ]
        
        layout = [
            [sg.MenuBar(menu_def)],
            toolbar,
            [sg.HSeparator()],
            [sg.Column(tools_tabs, vertical_alignment='top'),
             sg.VSeparator(),
             sg.Column(image_display, justification='center')],
            [sg.StatusBar('Prêt', key='STATUS')]
        ]
        
        return layout
    
    def update_image_info(self, window):
        """Met à jour les informations de l'image"""
        if self.current_image and self.current_file:
            filename = os.path.basename(self.current_file)
            window['FILE_INFO'].update(filename)
            
            width, height = self.current_image.size
            window['SIZE_INFO'].update(f'{width} x {height}')
            window['MODE_INFO'].update(self.current_image.mode)
            
            # Taille du fichier
            try:
                file_size = os.path.getsize(self.current_file)
                if file_size < 1024:
                    size_str = f'{file_size} B'
                elif file_size < 1024**2:
                    size_str = f'{file_size/1024:.1f} KB'
                else:
                    size_str = f'{file_size/1024**2:.1f} MB'
                window['FILE_SIZE'].update(size_str)
            except:
                window['FILE_SIZE'].update('N/A')
            
            # Mettre à jour les champs de redimensionnement
            window['RESIZE_WIDTH'].update(str(width))
            window['RESIZE_HEIGHT'].update(str(height))
            window['CROP_RIGHT'].update(str(width))
            window['CROP_BOTTOM'].update(str(height))
    
    def run(self):
        window = sg.Window('Éditeur d\'Images Avancé', self.create_layout(),
                          finalize=True, resizable=True, size=(1400, 900))
        
        # Variables pour les ajustements en temps réel
        last_brightness = 1.0
        last_contrast = 1.0
        last_color = 1.0
        
        while True:
            event, values = window.read(timeout=100)
            
            if event == sg.WIN_CLOSED or event == 'Quitter::CTRL+Q':
                break
            
            elif event == 'Ouvrir::CTRL+O' or event == 'OPEN':
                filename = sg.popup_get_file('Ouvrir une image',
                                           file_types=(("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),))
                if filename and self.load_image(filename):
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
                    self.update_image_info(window)
                    window['STATUS'].update(f'Image chargée: {os.path.basename(filename)}')
                    
                    # Réinitialiser les sliders
                    window['BRIGHTNESS'].update(1.0)
                    window['CONTRAST'].update(1.0)
                    window['COLOR'].update(1.0)
                    last_brightness = last_contrast = last_color = 1.0
            
            elif event in ['Sauvegarder::CTRL+S', 'SAVE']:
                if self.current_image and self.current_file:
                    try:
                        self.current_image.save(self.current_file)
                        sg.popup('Image sauvegardée!')
                    except Exception as e:
                        sg.popup_error(f'Erreur de sauvegarde: {str(e)}')
            
            elif event == 'Sauvegarder sous::CTRL+SHIFT+S':
                if self.current_image:
                    filename = sg.popup_get_file('Sauvegarder sous', save_as=True,
                                               file_types=(("PNG", "*.png"), ("JPEG", "*.jpg")))
                    if filename:
                        try:
                            self.current_image.save(filename)
                            self.current_file = filename
                            sg.popup('Image sauvegardée!')
                        except Exception as e:
                            sg.popup_error(f'Erreur de sauvegarde: {str(e)}')
            
            elif event == 'Annuler::CTRL+Z' or event == 'UNDO':
                if self.undo():
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
                    window['STATUS'].update('Action annulée')
            
            elif event == 'Refaire::CTRL+Y' or event == 'REDO':
                if self.redo():
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
                    window['STATUS'].update('Action refaite')
            
            elif event == 'Réinitialiser':
                if self.original_image:
                    self.current_image = self.original_image.copy()
                    self.save_to_history()
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
                    window['BRIGHTNESS'].update(1.0)
                    window['CONTRAST'].update(1.0)
                    window['COLOR'].update(1.0)
                    window['STATUS'].update('Image réinitialisée')
            
            # Filtres
            elif event.startswith('FILTER_'):
                filter_name = event.split('_')[1].lower()
                if self.apply_filter(filter_name):
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
                    window['STATUS'].update(f'Filtre {filter_name} appliqué')
            
            elif event == 'GRAYSCALE':
                if self.convert_to_grayscale():
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
                    window['STATUS'].update('Converti en niveaux de gris')
            
            # Rotations et miroirs
            elif event == 'ROTATE_LEFT':
                if self.rotate_image(-90):
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
                    self.update_image_info(window)
            
            elif event == 'ROTATE_RIGHT':
                if self.rotate_image(90):
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
                    self.update_image_info(window)
            
            elif event == 'FLIP_H':
                if self.flip_image('horizontal'):
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
            
            elif event == 'FLIP_V':
                if self.flip_image('vertical'):
                    image_bytes = self.image_to_bytes(self.current_image)
                    window['IMAGE_DISPLAY'].update(data=image_bytes)
            
            # Ajustements en temps réel
            elif event == 'BRIGHTNESS':
                current_brightness = values['BRIGHTNESS']
                if abs(current_brightness - last_brightness) > 0.1:
                    if self.original_image:
                        # Réappliquer depuis l'original avec tous les ajustements
                        temp_image = self.original_image.copy()
                        
                        # Appliquer luminosité
                        enhancer = ImageEnhance.Brightness(temp_image)
                        temp_image = enhancer.enhance(current_brightness)
                        
                        # Appliquer contraste
                        enhancer = ImageEnhance.Contrast(temp_image)
                        temp_image = enhancer.enhance(values['CONTRAST'])
                        
                        # Appliquer couleur
                        enhancer = ImageEnhance.Color(temp_image)
                        temp_image = enhancer.enhance(values['COLOR'])
                        
                        self.current_image = temp_image
                        image_bytes = self.image_to_bytes(self.current_image)
                        window['IMAGE_DISPLAY'].update(data=image_bytes)
                        
                    last_brightness = current_brightness
            
            elif event == 'CONTRAST':
                current_contrast = values['CONTRAST']
                if abs(current_contrast - last_contrast) > 0.1:
                    if self.original_image:
                        temp_image = self.original_image.copy()
                        
                        enhancer = ImageEnhance.Brightness(temp_image)
                        temp_image = enhancer.enhance(values['BRIGHTNESS'])
                        
                        enhancer = ImageEnhance.Contrast(temp_image)
                        temp_image = enhancer.enhance(current_contrast)
                        
                        enhancer = ImageEnhance.Color(temp_image)
                        temp_image = enhancer.enhance(values['COLOR'])
                        
                        self.current_image = temp_image
                        image_bytes = self.image_to_bytes(self.current_image)
                        window['IMAGE_DISPLAY'].update(data=image_bytes)
                        
                    last_contrast = current_contrast
            
            elif event == 'COLOR':
                current_color = values['COLOR']
                if abs(current_color - last_color) > 0.1:
                    if self.original_image:
                        temp_image = self.original_image.copy()
                        
                        enhancer = ImageEnhance.Brightness(temp_image)
                        temp_image = enhancer.enhance(values['BRIGHTNESS'])
                        
                        enhancer = ImageEnhance.Contrast(temp_image)
                        temp_image = enhancer.enhance(values['CONTRAST'])
                        
                        enhancer = ImageEnhance.Color(temp_image)
                        temp_image = enhancer.enhance(current_color)
                        
                        self.current_image = temp_image
                        image_bytes = self.image_to_bytes(self.current_image)
                        window['IMAGE_DISPLAY'].update(data=image_bytes)
                        
                    last_color = current_color
            
            # Transformations
            elif event == 'APPLY_ROTATION':
                try:
                    angle = float(values['ROTATION_ANGLE'])
                    if self.rotate_image(angle):
                        image_bytes = self.image_to_bytes(self.current_image)
                        window['IMAGE_DISPLAY'].update(data=image_bytes)
                        self.update_image_info(window)
                except ValueError:
                    sg.popup_error('Angle de rotation invalide')
            
            elif event == 'APPLY_RESIZE':
                try:
                    width = int(values['RESIZE_WIDTH'])
                    height = int(values['RESIZE_HEIGHT'])
                    maintain_aspect = values['MAINTAIN_ASPECT']
                    
                    if self.resize_image(width, height, maintain_aspect):
                        image_bytes = self.image_to_bytes(self.current_image)
                        window['IMAGE_DISPLAY'].update(data=image_bytes)
                        self.update_image_info(window)
                        window['STATUS'].update(f'Image redimensionnée: {width}x{height}')
                except ValueError:
                    sg.popup_error('Dimensions invalides')
            
            elif event == 'APPLY_CROP':
                try:
                    left = int(values['CROP_LEFT'])
                    top = int(values['CROP_TOP'])
                    right = int(values['CROP_RIGHT'])
                    bottom = int(values['CROP_BOTTOM'])
                    
                    if self.crop_image(left, top, right, bottom):
                        image_bytes = self.image_to_bytes(self.current_image)
                        window['IMAGE_DISPLAY'].update(data=image_bytes)
                        self.update_image_info(window)
                        window['STATUS'].update('Image recadrée')
                except ValueError:
                    sg.popup_error('Coordonnées de recadrage invalides')
            
            elif event == 'ADD_TEXT':
                text = values['TEXT_CONTENT']
                if text:
                    try:
                        x = int(values['TEXT_X'])
                        y = int(values['TEXT_Y'])
                        size = int(values['TEXT_SIZE'])
                        
                        color_map = {
                            'Blanc': (255, 255, 255),
                            'Noir': (0, 0, 0),
                            'Rouge': (255, 0, 0),
                            'Vert': (0, 255, 0),
                            'Bleu': (0, 0, 255)
                        }
                        color = color_map.get(values['TEXT_COLOR'], (255, 255, 255))
                        
                        if self.add_text(text, x, y, size, color):
                            image_bytes = self.image_to_bytes(self.current_image)
                            window['IMAGE_DISPLAY'].update(data=image_bytes)
                            window['STATUS'].update('Texte ajouté')
                    except ValueError:
                        sg.popup_error('Paramètres de texte invalides')
            
            elif event == 'UPDATE_HISTOGRAM':
                if self.current_image:
                    histogram_bytes = self.create_histogram_plot()
                    if histogram_bytes:
                        window['HISTOGRAM'].update(data=histogram_bytes)
                        window['STATUS'].update('Histogramme mis à jour')
            
            elif event == 'Informations':
                if self.current_image:
                    info_text = f"""
                    Informations sur l'image:
                    
                    Fichier: {os.path.basename(self.current_file) if self.current_file else 'Non sauvegardé'}
                    Dimensions: {self.current_image.size[0]} x {self.current_image.size[1]} pixels
                    Mode: {self.current_image.mode}
                    Format: {self.current_image.format if hasattr(self.current_image, 'format') else 'N/A'}
                    
                    Historique: {len(self.image_history)} états
                    Position actuelle: {self.history_index + 1}
                    """
                    sg.popup_scrolled(info_text, title='Informations Image')
            
            elif event == 'À propos':
                sg.popup('Éditeur d\'Images Avancé v6.0\n\n'
                        'Développé avec PySimpleGUI4 et PIL\n\n'
                        'Fonctionnalités:\n'
                        '• Filtres et effets\n'
                        '• Ajustements luminosité/contraste/couleur\n'
                        '• Rotations et transformations\n'
                        '• Ajout de texte\n'
                        '• Historique d\'actions\n'
                        '• Histogramme des couleurs',
                        title='À propos')
        
        window.close()

if __name__ == '__main__':
    editor = ImageEditor()
    editor.run()