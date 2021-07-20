import '@mdi/font/css/materialdesignicons.css';
import Vue from 'vue';
import Vuetify from 'vuetify/lib';

Vue.use( Vuetify );

/**
 * Vuetify theme system configuration.
 *
 * See metawiki for our visual style guidelines:
 * https://meta.wikimedia.org/wiki/Toolhub/Decision_record#Visual_Style
 */
export default new Vuetify( {
	theme: {
		options: {
			customProperties: true
		},
		themes: {
			light: {
				/* Vuetify theme settings */
				primary: '#36c', /* WMF: accent50 */
				secondary: '#202122', /* WMF: base10 */
				accent: '#f8f9fa', /* WMF: base90 */
				error: '#d33', /* WMF: red50 */
				info: '#fef6e7', /* WMF: yellow90 */
				success: '#00af89', /* WMF: green50 */
				warning: '#fc3', /* WMF: yellow50 */

				/* Additional Wikimedia style guide colors by name */
				base10: '#202122',
				base20: '#54595d',
				base80: '#e0e0e0',
				base90: '#f8f9fa',
				base100: '#fff',
				accent90: '#eaf3ff',
				accent50: '#36c',
				red50: '#d33',
				green50: '#00af89',
				yellow30: '#ac6600',
				yellow50: '#fc3',
				yellow90: '#fef6e7'
			}
		}
	}
} );
