'use strict';
import chai from 'chai';

const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { normalizeEmpty, computeChangeInfo, expandObjects } from './diff';

describe( 'helpers/diff', () => {
	describe( 'computeChangeInfo', () => {
		const formatProp = function ( property, value ) {
			return value;
		};

		it( 'should handle all operation types', () => {
			const basis = {
				scalar: 'hello',
				array: [ 'foo', 'bar', 'baz' ]
			};
			const ops = [
				// Yes, we know these operations are mostly nonsense from the
				// point of view of a real diff. They are designed for code path
				// coverage rather than real world usage.
				{ op: 'add', path: '/array/3', value: 'xyzzy' },
				{ op: 'copy', path: '/array/4', from: '/array/0' },
				{ op: 'move', path: '/array/0', from: '/array/1' },
				{ op: 'remove', path: '/array/1' },
				{ op: 'replace', path: '/scalar', value: 'goodbye' }
			];
			const expected = [
				{
					path: [ 'array', 0 ],
					oldValue: 'foo',
					newValue: 'bar'
				},
				{
					path: [ 'array', 1 ],
					oldValue: 'bar',
					newValue: null
				},
				{
					path: [ 'array', 1 ],
					oldValue: 'baz',
					newValue: 'xyzzy'
				},
				{
					path: [ 'array', 3 ],
					oldValue: null,
					newValue: 'xyzzy'
				},
				{
					path: [ 'array', 4 ],
					oldValue: null,
					newValue: 'foo'
				},
				{
					path: [ 'scalar' ],
					oldValue: 'hello',
					newValue: 'goodbye'
				}
			];
			const ci = computeChangeInfo( ops, basis, formatProp );
			expect( ci ).to.eql( expected );
		} );
		it( 'should handle nested objects', () => {
			const basis = {
				nested: {
					scalar: 'hello',
					array: [ 'foo' ]
				}
			};
			const ops = [
				{ op: 'replace', path: '/nested/scalar', value: 'goodbye' },
				{ op: 'replace', path: '/nested/array/0', value: 'bar' },
				{ op: 'add', path: '/nested/array/1', value: 'baz' }
			];
			const expected = [
				{
					path: [ 'nested', 'array', 0 ],
					oldValue: 'foo',
					newValue: 'bar'
				},
				{
					path: [ 'nested', 'array', 1 ],
					oldValue: null,
					newValue: 'baz'
				},
				{
					path: [ 'nested', 'scalar' ],
					oldValue: 'hello',
					newValue: 'goodbye'
				}
			];
			const ci = computeChangeInfo( ops, basis, formatProp );
			expect( ci ).to.eql( expected );
		} );
		it( 'should handle list element deletions', () => {
			const basis = {
				tools: [ 'tool1', 'tool2', 'tool3' ]
			};
			const ops = [
				{ op: 'remove', path: '/tools/0' },
				{ op: 'remove', path: '/tools/0' }
			];
			const expected = [
				{
					path: [ 'tools', 0 ],
					oldValue: 'tool1',
					newValue: 'tool2'
				},
				{
					path: [ 'tools', 0 ],
					oldValue: 'tool2',
					newValue: 'tool3'
				}
			];
			const ci = computeChangeInfo( ops, basis, formatProp );
			expect( ci ).to.eql( expected );
		} );
		it( 'should handle lists becoming empty', () => {
			const basis = {
				tools: [ 'tool1' ]
			};
			const ops = [
				{ op: 'remove', path: '/tools/0' }
			];
			const expected = [
				{
					path: [ 'tools', 0 ],
					oldValue: 'tool1',
					newValue: null
				}
			];
			const ci = computeChangeInfo( ops, basis, formatProp );
			expect( ci ).to.eql( expected );
		} );
	} );

	describe( 'normalizeEmpty', () => {
		it( 'should normalize empty things to null', () => {
			expect( normalizeEmpty( undefined ) ).to.be.null;
			expect( normalizeEmpty( null ) ).to.be.null;
			expect( normalizeEmpty( '' ) ).to.be.null;
			expect( normalizeEmpty( {} ) ).to.be.null;
			expect( normalizeEmpty( [] ) ).to.be.null;
		} );
		it( 'should pass through non-empty things', () => {
			expect( normalizeEmpty( ' ' ) ).to.equal( ' ' );
			expect( normalizeEmpty( { foo: 1 } ) ).to.eql( { foo: 1 } );
			expect( normalizeEmpty( [ 0 ] ) ).to.eql( [ 0 ] );
		} );
	} );

	describe( 'expandObjects', () => {
		it( 'should expand oldValue arrays', () => {
			const given = {
				path: [ 'members' ],
				oldValue: [ 'Fat Mike', 'Melvin', 'Smelly', 'El Hefe' ],
				newValue: undefined
			};
			const expected = [
				{
					path: [ 'members', 0 ],
					oldValue: 'Fat Mike',
					newValue: undefined
				},
				{
					path: [ 'members', 1 ],
					oldValue: 'Melvin',
					newValue: undefined
				},
				{
					path: [ 'members', 2 ],
					oldValue: 'Smelly',
					newValue: undefined
				},
				{
					path: [ 'members', 3 ],
					oldValue: 'El Hefe',
					newValue: undefined
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
		it( 'should expand newValue arrays', () => {
			const given = {
				path: [ 'members' ],
				oldValue: undefined,
				newValue: [ 'Fat Mike', 'Melvin', 'Smelly', 'El Hefe' ]
			};
			const expected = [
				{
					path: [ 'members', 0 ],
					oldValue: undefined,
					newValue: 'Fat Mike'
				},
				{
					path: [ 'members', 1 ],
					oldValue: undefined,
					newValue: 'Melvin'
				},
				{
					path: [ 'members', 2 ],
					oldValue: undefined,
					newValue: 'Smelly'
				},
				{
					path: [ 'members', 3 ],
					oldValue: undefined,
					newValue: 'El Hefe'
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
		it( 'should expand oldValue objects', () => {
			const given = {
				path: [ 'annotations' ],
				oldValue: { foo: 'foo', bar: 'bar' },
				newValue: undefined
			};
			const expected = [
				{
					path: [ 'annotations', 'foo' ],
					oldValue: 'foo',
					newValue: undefined
				},
				{
					path: [ 'annotations', 'bar' ],
					oldValue: 'bar',
					newValue: undefined
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
		it( 'should expand newValue objects', () => {
			const given = {
				path: [ 'annotations' ],
				oldValue: undefined,
				newValue: { foo: 'foo', bar: 'bar' }
			};
			const expected = [
				{
					path: [ 'annotations', 'foo' ],
					oldValue: undefined,
					newValue: 'foo'
				},
				{
					path: [ 'annotations', 'bar' ],
					oldValue: undefined,
					newValue: 'bar'
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
		it( 'should expand nested objects and arrays', () => {
			const given = {
				path: [ 'thing' ],
				oldValue: undefined,
				newValue: { foo: 'foo', bar: [ 0, 1 ], baz: [ { xyzzy: 1 } ] }
			};
			const expected = [
				{
					path: [ 'thing', 'foo' ],
					oldValue: undefined,
					newValue: 'foo'
				},
				{
					path: [ 'thing', 'bar', 0 ],
					oldValue: undefined,
					newValue: 0
				},
				{
					path: [ 'thing', 'bar', 1 ],
					oldValue: undefined,
					newValue: 1
				},
				{
					path: [ 'thing', 'baz', 0, 'xyzzy' ],
					oldValue: undefined,
					newValue: 1
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
		it( 'should generate the correct path when replacing an object with an object', () => {
			const given = {
				path: [ 'author', 0 ],
				oldValue: { name: 'Me' },
				newValue: { name: 'Buddy' }
			};
			const expected = [
				{
					path: [ 'author', 0, 'name' ],
					oldValue: 'Me',
					newValue: 'Buddy'
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
		it( 'should generate the correct path when replacing an array with an array', () => {
			const given = {
				path: [ 'array' ],
				oldValue: [ 'old' ],
				newValue: [ 'new' ]
			};
			const expected = [
				{
					path: [ 'array', 0 ],
					oldValue: 'old',
					newValue: 'new'
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
		it( 'should generate the correct change when replacing an object with a more detailed object', () => {
			const given = {
				path: [ 'author', 0 ],
				oldValue: { name: 'Me' },
				newValue: { name: 'Buddy', url: 'https://example.org/' }
			};
			const expected = [
				{
					path: [ 'author', 0, 'name' ],
					oldValue: 'Me',
					newValue: 'Buddy'
				},
				{
					path: [ 'author', 0, 'url' ],
					oldValue: undefined,
					newValue: 'https://example.org/'
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
		it( 'should generate the correct change when replacing an object with a less detailed object', () => {
			const given = {
				path: [ 'author', 0 ],
				oldValue: { name: 'Me', url: 'https://example.org/' },
				newValue: { name: 'Buddy' }
			};
			const expected = [
				{
					path: [ 'author', 0, 'name' ],
					oldValue: 'Me',
					newValue: 'Buddy'
				},
				{
					path: [ 'author', 0, 'url' ],
					oldValue: 'https://example.org/',
					newValue: undefined
				}
			];
			const expanded = expandObjects( given );
			expect( expanded ).to.eql( expected );
		} );
	} );
} );
