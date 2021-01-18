import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import i18n from './plugins/i18n';
import notify from './plugins/notify';

Vue.config.productionTip = false;

Vue.use( notify, { store: store } );

new Vue( {
	vuetify,
	router,
	store,
	i18n,
	render: ( h ) => h( App )
} ).$mount( '#app' );
