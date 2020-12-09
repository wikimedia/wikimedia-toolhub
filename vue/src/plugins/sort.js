export function sortByAlphabeticalOrder( aIndex, bIndex, isDesc ) {
	if ( !isDesc[ 0 ] ) {
		if ( aIndex > bIndex ) {
			return -1;
		}
		if ( aIndex < bIndex ) {
			return 1;
		}
	} else {
		if ( aIndex < bIndex ) {
			return -1;
		}
		if ( aIndex > bIndex ) {
			return 1;
		}
	}
	return 0;
}

export function sortByNumbers( aIndex, bIndex, isDesc ) {
	if ( !isDesc[ 0 ] ) {
		return aIndex - bIndex;
	} else {
		return bIndex - aIndex;
	}
}

export function sortByDates( aIndex, bIndex, isDesc ) {
	if ( !isDesc[ 0 ] ) {
		return new Date( aIndex ) - new Date( bIndex );
	} else {
		return new Date( bIndex ) - new Date( aIndex );
	}
}

export function customSort( items, index, isDesc ) {
	items.sort( ( a, b ) => {
		let aIndex = a[ index ],
			bIndex = b[ index ];

		if (
			index[ 0 ] === 'end_date' ||
			index[ 0 ] === 'created_date' ||
			index[ 0 ] === 'url.created_date' ) {
			if ( index[ 0 ] === 'url.created_date' ) {
				aIndex = a.url.created_date;
				bIndex = b.url.created_date;
			}

			return sortByDates( aIndex, bIndex, isDesc );
		}

		if ( index[ 0 ] === 'urls.count' ) {
			aIndex = a.urls.count;
			bIndex = b.urls.count;

			return sortByNumbers( aIndex, bIndex, isDesc );
		}

		if ( index[ 0 ] === 'url.created_by.username' ||
			index[ 0 ] === 'url.url' ) {
			if ( index[ 0 ] === 'url.created_by.username' ) {
				aIndex = a.url.created_by.username;
				bIndex = b.url.created_by.username;
			}

			if ( index[ 0 ] === 'url.url' ) {
				aIndex = a.url.url;
				bIndex = b.url.url;
			}

			return sortByAlphabeticalOrder( aIndex, bIndex, isDesc );
		}

		return sortByNumbers( aIndex, bIndex, isDesc );
	} );
	return items;
}

export default customSort;
