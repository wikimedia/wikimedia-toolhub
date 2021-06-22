/* eslint-disable no-unused-expressions */
/* eslint-disable no-unused-vars */
'use strict';
import chai from 'chai';
import sinon from 'sinon';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;

import { shallowMount } from '@vue/test-utils';

import EventIcon from '@/components/auditlog/EventIcon';
import EventTimestamp from '@/components/auditlog/EventTimestamp';
import UserLink from '@/components/auditlog/UserLink';
import LogEvent from './LogEvent';

describe( 'components/auditlog', () => {
	describe( 'LogEvent', () => {
		it( 'tool-updated', () => {
			const event = {
				id: 1132,
				timestamp: '2021-06-11T23:04:46.956231Z',
				user: {
					id: 2,
					username: 'BDavis (WMF)'
				},
				target: {
					type: 'tool',
					id: 'test-20210514',
					label: 'test-20210514'
				},
				action: 'updated',
				params: {},
				message: '+developer_docs'
			};
			const $root = { $vuetify: { rtl: false } };
			const wrapper = shallowMount(
				LogEvent, {
					propsData: { log: event },
					computed: { isRTL: () => true }
				}
			);

			expect( wrapper ).to.be.an( 'object' );
			expect( wrapper.classes() ).to.contain( 'log-event' );
			expect( wrapper.classes() ).to.contain( 'row' );

			const icon = wrapper.findComponent( EventIcon );
			expect( icon.exists() ).to.be.true;

			const timestamp = wrapper.findComponent( EventTimestamp );
			expect( timestamp.exists() ).to.be.true;

			const userlink = wrapper.findComponent( UserLink );
			expect( userlink.exists() ).to.be.true;
			expect( userlink.html() ).to.contain( event.user.username );

			const tools = wrapper.findAll( '.log-event-tool' );
			expect( tools.length ).to.equal( 1 );
			expect( tools.at( 0 ).html() ).to.contain( event.target.label );
		} );
	} );
} );
