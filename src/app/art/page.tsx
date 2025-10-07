import { promises as fs } from 'fs';
import path from 'path';
import ArtGrid from '../../../components/ArtGrid';

interface ArtPiece {
  id: string;
  title: string;
  src: string;
  alt: string;
  year?: string;
  medium?: string;
  description?: string;
}

async function getArtPieces(): Promise<ArtPiece[]> {
  try {
    // Get art files from public/art directory
    const artDir = path.join(process.cwd(), 'public/art');
    const files = await fs.readdir(artDir);

    // Filter for image files
    const imageFiles = files.filter(file =>
      file.endsWith('.png') ||
      file.endsWith('.jpg') ||
      file.endsWith('.jpeg') ||
      file.endsWith('.gif') ||
      file.endsWith('.webp') ||
      file.endsWith('.JPG') ||
      file.endsWith('.PNG')
    );

    // Create art pieces from files
    const artPieces: ArtPiece[] = imageFiles.map((file, index) => {
      const name = file.replace(/\.[^/.]+$/, ''); // Remove extension
      const id = `art-${index + 1}`;

      return {
        id,
        title: `Artwork ${index + 1}`,
        src: `/art/${file}`,
        alt: `Art piece by Daniel Kliewer - ${name}`,
        year: '2025',
        medium: 'Digital Art',
        description: 'A piece exploring the intersection of technology and creativity.',
      };
    });

    console.log(`Loaded ${artPieces.length} art pieces from directory`);
    return artPieces;
  } catch (error) {
    console.error('Error loading art pieces:', error);
    // Return fallback art pieces using existing files
    return [
      {
        id: 'art-1',
        title: 'Digital Composition 1',
        src: '/art/20221003_170829.jpg',
        alt: 'Digital artwork by Daniel Kliewer',
        year: '2022',
        medium: 'Photography',
        description: 'An exploration of light and form in digital photography.',
      },
      {
        id: 'art-2',
        title: 'Digital Composition 2',
        src: '/art/AfterlightImage1.jpg',
        alt: 'Digital artwork by Daniel Kliewer',
        year: '2022',
        medium: 'Digital Art',
        description: 'Abstract representation created with digital tools.',
      },
      {
        id: 'art-3',
        title: 'Digital Composition 3',
        src: '/art/IMG_0004.JPG',
        alt: 'Digital artwork by Daniel Kliewer',
        year: '2023',
        medium: 'Photography',
        description: 'Visual interpretation of everyday moments.',
      },
    ];
  }
}

export default async function ArtPage() {
  const artPieces = await getArtPieces();

  return (
    <div>
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white sm:text-5xl">
            Art Gallery
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
            My visual work explores the intersection of technology and material practice — paintings, digital works, and experimental pieces that bridge the digital and physical worlds.
          </p>
        </div>

        {/* Art Grid */}
        <ArtGrid artPieces={artPieces} />

        {/* Artist Statement */}
        <div className="mt-16 max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Artist Statement
          </h2>
          <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
            My work investigates the liminal spaces between human creativity and machine intelligence.
            Through digital tools and traditional mediums, I explore how technology shapes our perception of art,
            identity, and reality itself. Each piece is an experiment in collaboration between human intention
            and algorithmic possibility.
          </p>
        </div>
      </div>
    </div>
  );
}
