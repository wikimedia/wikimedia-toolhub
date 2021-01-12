import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import i18n from './plugins/i18n';
import notify from './plugins/notify';
import clipboard from 'vue-clipboard2';

Vue.config.productionTip = false;
Vue.use( notify, { store: store } );
Vue.use( clipboard );

new Vue( {
	vuetify,
	router,
	store,
	i18n,
	render: ( h ) => h( App )
} ).$mount( '#app' );
