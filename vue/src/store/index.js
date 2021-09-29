import Vue from 'vue';
import Vuex from 'vuex';

import ApiModule from './api';
import AuditLogsModule from './auditlogs';
import CrawlerModule from './crawler';
import FavoritesModule from './favorites';
import GroupsModule from './groups';
import ListsModule from './lists';
import LocaleModule from './locale';
import OauthModule from './oauth';
import SearchModule from './search';
import ToolsModule from './tools';
import UIModule from './ui';
import UserModule from './user';

/* istanbul ignore next: upstream tested */
Vue.use( Vuex );

export default new Vuex.Store( {
	modules: {
		api: ApiModule,
		auditlogs: AuditLogsModule,
		crawler: CrawlerModule,
		favorites: FavoritesModule,
		groups: GroupsModule,
		lists: ListsModule,
		locale: LocaleModule,
		oauth: OauthModule,
		search: SearchModule,
		tools: ToolsModule,
		ui: UIModule,
		user: UserModule
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
} );
