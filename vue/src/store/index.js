import Vue from 'vue';
import Vuex from 'vuex';

import ApiModule from './api';
import AuditLogsModule from './auditlogs';
import CrawlerModule from './crawler';
import LocaleModule from './locale';
import SearchModule from './search';
import ToolsModule from './tools';
import UserModule from './user';
import GroupsModule from './groups';
import ListsModule from './lists';

/* istanbul ignore next: upstream tested */
Vue.use( Vuex );

export default new Vuex.Store( {
	modules: {
		api: ApiModule,
		auditlogs: AuditLogsModule,
		crawler: CrawlerModule,
		locale: LocaleModule,
		search: SearchModule,
		tools: ToolsModule,
		user: UserModule,
		groups: GroupsModule,
		lists: ListsModule
	},
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
} );
