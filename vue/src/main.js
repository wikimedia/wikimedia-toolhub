import Vue from 'vue';
import AsyncComputed from 'vue-async-computed';
import clipboard from 'vue-clipboard2';
import Fragment from 'vue-fragment';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import i18n from './plugins/i18n';
import notify from './plugins/notify';

Vue.config.productionTip = false;
Vue.use( AsyncComputed );
Vue.use( clipboard );
Vue.use( Fragment.Plugin );
Vue.use( notify, { store: store } );

new Vue( {
	vuetify,
	router,
	store,
	i18n,
	render: ( h ) => h( App )
} ).$mount( '#app' );
