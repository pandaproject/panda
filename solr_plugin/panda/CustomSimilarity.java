package panda;
import org.apache.lucene.search.DefaultSimilarity;


public class CustomSimilarity extends DefaultSimilarity {
	public CustomSimilarity() {
	}
	public float tf(float freq) {
		return 1;
	}
	public float idf(int i, int i1) {
		return 1;
	}
}
